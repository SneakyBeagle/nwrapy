from nwrapy.colours import clr

def print_dict(d, level=0, div="-", start='|'):
    if type(d)==dict:
        for k,e in d.items():
            if type(k)==int:
                print(clr.BOLD_WHITE+start+level*div, k, clr.RESET)
            else:
                if level==0:
                    print('#'*10)
                    print(level*div+clr.GREEN+str(k), clr.RESET)
                elif level==1:
                    print('-'*10)
                    print(start+level*div+clr.FAINT_WHITE, k, clr.RESET)
                    print('-'*10)
                else:
                    print(start+level*div+clr.FAINT_WHITE, k, clr.RESET)
            print_dict(e, level+1)
    elif type(d)==list:
        for item in d:
            print_dict(item, level+1)
    else:
        print(start+(level)*div, d, clr.RESET)
