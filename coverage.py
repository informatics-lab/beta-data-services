class Coverage(object):
    """
    A coverage is a description of available data which can be requested from
    BDS, for a particular model variable. This variable is described by its
    name (and label), for example, UKPPBEST_High_cloud_cover.

    """
    def __init__(self, name=None, label=None, bbox=None, dim_runs=None,
                 dim_forecasts=None, times=None, elevations=None, CRSs=None,
                 formats=None, interpolations=None):
        self.name           = name
        self.label          = label
        self.bbox           = bbox
        self.dim_runs       = dim_runs
        self.dim_forecasts  = dim_forecasts
        self.times          = times
        self.elevations     = elevations
        self.CRSs           = CRSs
        self.formats        = formats
        self.interpolations = interpolations

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def _info_str(self, attr_name, as_list=False):
        """
        Format a single attribute for printing.

        """
        attr_val = getattr(self, attr_name)
        if attr_val is not None:
            if type(attr_val) == list:
                # Make sure all list items are strings so .join works.
                attr_val = [str(val) for val in attr_val]
                if as_list:
                    attr_val = ", ".join(attr_val)
                else:
                    attr_val = "\n".join(attr_val)
            else:
                attr_val = str(attr_val)

            return "*** " + attr_name.upper() + " ***\n" + \
                   attr_val + "\n\n"
        else:
            return ""

    def print_info(self):
        """
        Print out all infomation.

        """
        print_order = ["name", "label", "bbox", "dim_runs", "dim_forecasts",
                       "times", "elevations", "CRSs", "formats",
                       "interpolations"]
        # Some attributes are lists, but default is to print each item on a new
        # line. Specify which should be kept in one line (like a normal list
        # print)
        as_lists = ["bbox"]
        info_str = ""
        for attr_name in print_order:
            as_list = False
            if attr_name in as_lists:
                as_list = True
            info_str += self._info_str(attr_name, as_list)
        print info_str


class CoverageList(list):
    """
    List of coverages.

    TODO..
    Assert each item is a Coverage instance
    Any List methods to overwrite?

    """
    def __str__(self):
        print_str = ""
        for i, item in enumerate(self):
            print_str += "{i}: {item}\n".format(i=i, item=item)
        return print_str
