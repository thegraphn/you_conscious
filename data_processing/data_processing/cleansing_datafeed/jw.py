from pyjarowinkler import distance

s1="192221-1206336"
s2="1922sa21-1206333"

print(distance.get_jaro_distance(s1,s2))