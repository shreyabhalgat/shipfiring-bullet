n=input()
x=int(input())
for i in range (x):
    a=" "
    b=input()
    c=0
    d=0
    e=len(n)
    f=len(b)
    while c<e and d<f :
        if n[c]==[d]:
            a=a+n[c]
            c=c+1
            d=d+1
        else:
            c=c+1
    if a==b:
        print("positve")
    else:
        print("neagtive")