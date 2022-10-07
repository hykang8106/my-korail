# [ref] 
# https://www.linuxquestions.org/questions/programming-9/python-create-variables-from-dictionary-keys-859776/
#
# create variables from dictionary keys, and assign dictionary values to variables

"""
def my_func(key=None):
   print(key)
   #do the real stuff

temp = {'key': 'tttt'}

my_func(**temp)
"""

p = {'a' : '122', 'b' : '111111'}

for k, v in p.items():
   # exec("%s = %s" % (k, v))
   exec("{} = {}".format(k, v))

print(a, b)