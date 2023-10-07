config_model_category = {
    "PYTORCH_BASE_MODEL": "distilbert-base-multilingual-cased",
    "LOCAL_CSV_PATH": "/Users/levecq/private_repository/you_conscious/dl_xp/data/category/datafeed-2-1.csv",
    "INPUT_FEATURES": ["Title", "description"],
    "TARGET_FEATURE": "category_name",
    "DELIMITER": ";",
    "DIR_MODEL": "category_model",
    "MODEL_NAME": "category_model",
    "NUM_EPOCHS": 2,
    "MAX_LENGTH": 50,
    "BATCH_SIZE_TRAIN": 32,  # for 4 P100 GPUs
    "BATCH_SIZE_DEV": 32,  # for 4 P100 GPUs
    "BATCH_SIZE_TEST": 32,  # because we will predict with only 1 P100 GPU
    "PRED_BATCH_SIZE": 32,
}