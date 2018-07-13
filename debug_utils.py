import os, psutil, logging, platform, resource, time, sys

def log_rss_memory_usage(msg=''):
	max_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	if platform.system() == 'Darwin':
		max_rss = max_rss/1e6
	else:
		max_rss = max_rss/1e3

	rss = psutil.Process(os.getpid()).memory_info().rss
	thislog = logging.getLogger(__name__)
	thislog.info('Memory usage: {:.2f} MB. (Peak so far: {:.2f} MB) {}'.format(rss/1e6, max_rss, msg))

def get_memory_status():
	return psutil.virtual_memory()

def get_available_memory():
	return psutil.virtual_memory().available/1e6

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed

def get_script_path():
	return os.path.dirname(os.path.realpath(sys.argv[0]))
