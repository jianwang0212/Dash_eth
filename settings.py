import config
import ccxt


exchanges = {}

########
# bitbay #
########

exchanges['bitbay'] = {}
exchanges['bitbay']['init'] = ccxt.bitbay(config.bitbay)
exchanges['bitbay']['limit'] = 100
exchanges['bitbay']['currency'] = 'pln'
exchanges['bitbay']['name'] = 'bitbay'

###############
# indodax #
###############

exchanges['indodax'] = {}
exchanges['indodax']['init'] = ccxt.indodax(config.indodax)
exchanges['indodax']['limit'] = 500
exchanges['indodax']['currency'] = 'idr'
exchanges['indodax']['name'] = 'indodax'
