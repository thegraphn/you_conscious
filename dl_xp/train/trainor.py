"""Train model and save model to cloud storage"""

# pylint: disable=import-error,E1101


import glob
import os
import torch
from sklearn.metrics import classification_report
from torch import nn
from torch.optim import AdamW
from transformers import get_scheduler
from tqdm import tqdm
import matplotlib.pyplot as plt
import logging

class Trainor:
    """Trainor to class to train a Kop Model"""

    def __init__(self,config):
        """Trainor Constructor"""
        self.config = config
        self.setup()
        self.logger = logging.getLogger(__name__)

    def setup(self):
        """Setup method to create directories"""
        if not os.path.exists(self.config["DIR_MODEL"]):
            os.makedirs(self.config["DIR_MODEL"])


    def train(self, model, train_dataloader,  # pylint: disable= too-many-locals, too-many-statements
              dev_dataloader):
        """Train a model on train and dev data """

        self.logger.info("Start: train")
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.logger.info(f'Device used for training: {device}')

        model = nn.DataParallel(model).to(device)  # model.to(device)
        optimizer = AdamW(model.parameters(), lr=5e-5)

        num_training_steps = self.config.get('NUM_EPOCHS') * len(train_dataloader)
        self.logger.info(f'Number of training steps: {num_training_steps}')
        lr_scheduler = get_scheduler(
            name="linear",
            optimizer=optimizer,
            num_warmup_steps=0,
            num_training_steps=num_training_steps
        )

        # We train the model with earlystopping:
        # If the metric does not improve over 'patience' epochs, stop the training
        progress_bar = tqdm(range(num_training_steps))

        best_metric = 0  # Initialize with a large value for loss or a small value for f1
        epochs_since_improvement = 0
        patience = 5  # Number of epochs to wait for improvement before early stopping

        train_losses = []
        val_losses = []
        f1_scores = []
        best_model = model
        self.logger.info(f'Start training for {num_training_steps} steps.')

        for epoch in range(self.config.get('NUM_EPOCHS')):
            progress_bar.set_description(f'Epoch {epoch}/{self.config.get("NUM_EPOCHS")}')

            # training loop
            model.train()
            train_loss = 0.0
            num_batches = 0
            for batch in train_dataloader:
                # transfer data to GPU
                batch = {k: v.to(device) for k, v in batch.items()}
                # forward pass
                outputs = model(**batch)  # pylint: disable=E1102
                # find the loss
                loss = outputs.loss
                # calculate the gradients
                loss.sum().backward()
                # update the weights and learning rate
                optimizer.step()
                lr_scheduler.step()
                # clear the gradients
                optimizer.zero_grad()
                progress_bar.update(1)
                train_loss += loss.sum().item()
                num_batches += 1

            # Calculate the average training loss for the epoch
            avg_train_loss = train_loss / num_batches
            train_losses.append(avg_train_loss)

            # empty GPU cache
            torch.cuda.empty_cache()

            # validation loop
            model.eval()
            predictions = []  # List to store predicted labels
            ground_truths = []  # List to store ground truth labels
            val_loss = 0.0
            num_val_batches = 1
            for batch in dev_dataloader:
                # transfer data to GPU
                batch = {k: v.to(device) for k, v in batch.items()}
                # forward pass
                outputs = model(**batch)  # pylint: disable=E1102
                # find the loss
                valid_loss = outputs.loss
                # Get the predicted labels
                batch_predictions = torch.argmax(outputs.logits, dim=1).cpu().tolist()  # pylint: disable=no-member
                predictions.extend(batch_predictions)

                # Get the ground truth labels
                batch_ground_truths = batch['labels'].cpu().tolist()
                ground_truths.extend(batch_ground_truths)
                val_loss += valid_loss.sum().item()
                num_val_batches += 1

            # Calculate the average validation loss for the epoch
            avg_val_loss = val_loss / num_val_batches
            val_losses.append(avg_val_loss)

            classification_report_str = classification_report(
                ground_truths, predictions, output_dict=True)
            f1_score = classification_report_str['macro avg']['f1-score']
            f1_scores.append(f1_score)

            # Compare metric with the best metric value
            if f1_score > best_metric:
                best_metric = f1_score
                epochs_since_improvement = 0
                best_model = model
            else:
                epochs_since_improvement += 1

            # empty GPU cache
            torch.cuda.empty_cache()

            # Check if early stopping criteria are met
            if epochs_since_improvement >= patience:
                self.logger.info(
                    f"Early stopping triggered after {epochs_since_improvement} "
                    f"epochs without improvement.")
                break

        # plots over epochs
        self.create_plot(train_losses, 'train_loss')
        self.create_plot(val_losses, 'val_loss')
        self.create_plot(f1_scores, 'f1_macro')

        # print final metrics
        self.logger.info(f'Epoch {epoch + 1} -- Training Loss: {loss / len(train_dataloader)}, '
                         f'Validation Loss: {valid_loss / len(dev_dataloader)}')

        # save best model
        best_model.module.save_pretrained(self.config["DIR_MODEL"])
        self.logger.info("End: train")
        self.logger.info(f"Model saved to {self.config['DIR_MODEL']}")

    def store_to_cloud_storage(self, kop_model_suffix: str, model_id: str):
        """ Upload model's files to cloud storage"""
        gcs_destination = f"{kop_model_suffix}/{model_id}"
        list_files_to_upload = glob.glob(os.path.join(self.config["DIR_MODEL"], "*"))
        self.logger.info(f"Files to upload: {list_files_to_upload}")
        for file in tqdm(
                list_files_to_upload,
                desc="Uploading files to GCS",
                total=len(list_files_to_upload)):
            self.logger.info(f"Uploading file {file}")
            self.storage_client_models.upload_file(
                file, f"{kop_model_suffix}/{model_id}/{file.split('/')[-1]}")
        return f"{gcs_destination}"

    def create_plot(self, entity, metric_name):
        """Create metric plots"""
        self.logger.info(f'Creating plot for {metric_name} metric.')
        plt.plot(entity)
        plt.xlabel('Epoch')
        plt.ylabel(metric_name)
        plt.title(metric_name)
        plt.legend()
        plt.savefig(os.path.join(self.config["DIR_MODEL"], f'{metric_name}.png'))
        plt.close()