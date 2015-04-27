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


class CoverageList(object):
    """
    List of Coverages.

    Args:

    * coverages: list, tuple, Coverages
        Only Coverage list items aloud.

    """
    def __init__(self, *coverages):
        args_len = len(coverages)
        if args_len == 0:
            self.coverage_list = []
        elif args_len == 1:
            if type(coverages[0]) in [list, tuple]:
                self.coverage_list = list(coverages[0])
            elif type(coverages[0]) == Coverage:
                self.coverage_list = [coverages[0]]
            else:
                raise TypeError("CoverageList only accepts lists of Coverages"\
                                " or Coverages.")
        else:
            self.coverage_list = list(coverages)
        for item in self.coverage_list:
            if type(item) != Coverage:
                raise TypeError("%s is not a Coverage" % item)

    def __add__(self, other):
        if type(other) == list:
            other = CoverageList(other)
        elif type(other) != CoverageList:
            raise TypeError("Can not concatenate non list type object to a "\
                            "CoverageList.")
        return CoverageList(self.coverage_list + other.coverage_list)

    def __len__(self):
        return len(self.coverage_list)

    def __iter__(self):
        for item in self.coverage_list:
            yield item

    def __delitem__(self, key):
        self.coverage_list.__delitem__(key)

    def __getitem__(self, key):
        return self.coverage_list.__getitem__(key)

    def __setitem__(self, key, value):
        self.coverage_list.__setitem__(key, value)

    def __str__(self):
        print_covs = []
        for i, item in enumerate(self):
            print_covs.append("{i}: {item}".format(i=i, item=item))
        return "\n".join(print_covs)
