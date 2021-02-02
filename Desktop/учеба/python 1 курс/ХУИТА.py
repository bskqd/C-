class PDI:
    def __init__(self):
        self._d={}
        
    def __getitem__(self,key):
        return self._d[key]
    
    def __setitem__(self,key,value):
        if type(key)!=int:
            print('key must be integer')
            raise KeyError
        elif key in self._d:
            raise KeyError
        self._d[key]=value
        
    def __contains__(self,key):
        return key in self._d
    
    def __len__(self):
        return len(self._d)
    
    def __str__(self):
        return str(self._d)
    
    def __add__(self,other):
        d1=PDI()
        for i in self._d.keys():
            for j in other.keys():
                if i!=j:
                    d1.__setitem__(i,self._d[i])
                else:
                    d1.__setitem__(i,self._d[i])
                    d1.__setitem__(j,other.d[j])
        return d1
d=PDI()
d2=PDI()
d3=PDI()
d[1]=1
d2[2]=2
d3=d+d2
