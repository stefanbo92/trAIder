import matplotlib.pyplot as plt
from scipy.stats import bernoulli
import random

def bernoulli_trial(p: float) -> int:
    """Returns 1 with probability p and 0 with probability 1-p"""
    return 1 if random.random() < p else 0

def binomial(n: int, p: float) -> int:
    """Returns the sum of n bernoulli(p) trials"""
    return sum(bernoulli_trial(p) for _ in range(n))

# PARAMETERS
val_size=20
reported_accuracy=0.55
underlying_acc=0.5

dist=[]
win_cnt=0
for idx in range(10000):
    dist.append(binomial(val_size,underlying_acc))
    if(dist[-1]>=val_size*reported_accuracy):
        win_cnt+=1

print("probability for reported accuracy of",reported_accuracy,"while actual accuracy is",underlying_acc)
print(win_cnt/len(dist)*100,"%")
plt.hist(dist,100)
plt.show()
    
