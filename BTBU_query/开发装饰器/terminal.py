import time

def timmer(func):
    def warpper(*args,**kwargs):
        strat_time = time.time()
        back = func(*args,**kwargs)
        stop_time = time.time()
        print(f'\t函数 {func.__name__} 运行时间：\t{stop_time-strat_time}')
        return back
    return warpper