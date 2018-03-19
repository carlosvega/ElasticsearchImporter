import os, psutil, logging

def log_rss_memory_usage(msg=''):
	rss = psutil.Process(os.getpid()).memory_info().rss
	thislog = logging.getLogger(__name__)
	thislog.info('Memory usage: {:.2f} MB. {}'.format(rss/1e6, msg))