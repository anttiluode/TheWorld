import numpy as np

def main():
    t=np.linspace(0,20,2001)
    mono=np.exp(-0.2*t)
    print('scalar exponential RMSE',np.sqrt(np.mean((mono-np.exp(-0.2*t))**2)))
    alpha=0.12
    omega=2*np.pi*0.35
    target=np.exp(-alpha*t)*np.cos(omega*t)
    zc=int(np.sum(np.signbit(target[:-1]) != np.signbit(target[1:])))
    print('target sign changes',zc)
    for K in (1,2,4,8,16,32,64):
        rates=np.geomspace(0.03,5.0,K)
        X=np.exp(-np.outer(t,rates))
        ridge=1e-8
        c=np.linalg.solve(X.T@X+ridge*np.eye(K),X.T@target)
        pred=X@c
        rmse=float(np.sqrt(np.mean((pred-target)**2)))
        print(K,rmse,float(np.max(np.abs(c))))
    resonant=np.exp(-alpha*t)*np.cos(omega*t)
    print('two-state rotation RMSE',float(np.sqrt(np.mean((resonant-target)**2))))

if __name__=='__main__':
    main()
