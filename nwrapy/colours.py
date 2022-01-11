
class colours():
    def __init__(self):
        self.RESET = '\033[0m'
        self.BOLD = '\033[1m'
        self.DIM = '\033[2m'
        self.ITALIC = '\033[3m'
        self.UNDERLINE = '\033[4m'
        self.BLINK = '\033[5m'
        self.BLINK2 = '\033[6m'
        self.BACKGROUND = '\033[7m'
        self.INVISIBLE = '\033[8m'
        self.CROSSED = '\033[9m'
        
        self.DOUBLEUNDERLINE='\033[21m'
        
        self.BOLD_WHITE = '\033[1m\033[37m'
        self.FAINT_WHITE = '\033[2m\033[37m'
        
        self.BLACK = '\033[30m'
        self.RED = '\033[31m'
        self.GREEN = '\033[32m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.PURPLE = '\033[35m'
        self.LIGHTBLUE = '\033[36m'
        self.GREY = '\033[37m'

    def help(self):
        print(self.__dict__)

    def get_all(self):
        return self.__dict__

    def test2(self):
        for k,v in self.get_all().items():
            print(k, v, v.split('\0'), self.RESET)
    
    def test(self):
        #print(dir(self))
        # Styles
        for i in range(0,10):
            print('\033['+str(i)+'m'+'\\033['+str(i)+'m'+self.RESET)

        # Colours
        for i in range(0,10):
            print('\033[3'+str(i)+'m'+'\\033[3'+str(i)+'m'+self.RESET)

        
        for i in range(0,10):
            print('\033[2'+str(i)+'m'+'\\033[2'+str(i)+'m'+self.RESET)
        

clr=colours()

if __name__=='__main__':
    clr.help()
    clr.test()
    clr.test2()
