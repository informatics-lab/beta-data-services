"""
Module to get data from Met Office Beta Data Services.
This is a simple extension of the webcoverageservice module. See
webcoverageservice for most documentation.

"""
import webcoverageservice as wcs

VALID_MODEL_FEEDS = ["EGloEGRR",
                     "UKPPBEST",
                     "UKPPNOW",
                     "EURO4",
                     "GlobEGRR"]

def _get_url(model_feed):
    """
    Build the BDS url for the given model feed.

    """
    _check_model_feed(model_feed)
    bds_url = "https://dataservices-beta.metoffice.gov.uk/services/"
    return bds_url + model_feed

def _check_model_feed(model_feed):
    if model_feed not in VALID_MODEL_FEEDS:
        raise UserWarning("%s is an invalid model feed. Valid model feeds"\
                          " are %s" % (model_feed,
                                       VALID_MODEL_FEEDS.join("/n")))

class WCS1Requester(wcs.WCS1Requester):
    """
    For WCS verion 1.0 requests to beta data services (BDS).

    Args:

    * api_key: string
        BDS requires an api key to access the data. This is can received by
        signing up to Met Office DataPoint. www.metoffice.gov.uk/datapoint/

    Kwargs:

    * model_feed: string
        The model feed from which you wish to pull data.

    * validate_api: boolean
        If True a dummy request is made during intialisation to check the api
        key is valid. This is not entirely necessary as the same check is done
        with all requests.

    """
    def __init__(self, api_key, model_feed, validate_api=False):
        url = _get_url(model_feed)
        super(WCS1Requester, self).__init__(url, api_key, validate_api)

class WCS2Requester(wcs.WCS2Requester):
    """
    For WCS verion 2.0.0 requests to beta data services (BDS).

    Args:

    * api_key: string
        BDS requires an api key to access the data. This is can received by
        signing up to Met Office DataPoint. www.metoffice.gov.uk/datapoint/

    Kwargs:

    * model_feed: string
        The model feed from which you wish to pull data.

    * validate_api: boolean
        If True a dummy request is made during intialisation to check the api
        key is valid. This is not entirely necessary as the same check is done
        with all requests.

    """
    def __init__(self, api_key, model_feed, validate_api=False):
        url = _get_url(model_feed)
        super(WCS2Requester, self).__init__(url, api_key, validate_api)
