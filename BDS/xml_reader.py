import xml.etree.ElementTree as ET
from coverage import Coverage, CoverageList

# Defaults
xmlns = "{http://www.opengis.net/wcs}"
err_xmlns = "{http://www.opengis.net/ows}"

########## Generic functions ##########

def getElements(path, root, single_elem=False, namespace=None):
    """
    Extract elements at given xml path.

    Args:

    * path: string
        The path (in terms of nested elements) to the required element.

    * root: xml.etree.ElementTree.Element
        The element from which the given path starts.

    Kwargs:

    * single_elem: boolean
        If True, this raises an error if more than one element is found. It
        also changes the return type to a single value (instead of list).

    * namespace: string or None
        The xml namespace for the given path.

    returns:
        Single (if single_elem=True) or list of xml.etree.ElementTree.Element
        object(s).

    """
    if namespace:
        path  = path.split('/')
        path = [namespace + elem_name for elem_name in path]
        path = "/".join(path)
    elems = root.findall(path)

    if single_elem:
        if len(elems) == 1:
            return elems[0]
        else:
            raise UserWarning("Expected to find exactly 1 {path} element,"\
                              " but found {fnd} instead."\
                              .format(path=path, fnd=len(elems)))
    else:
        return elems

def getElementsText(path, root, single_elem=False, namespace=None):
    """
    Extract elements' text at given xml path.

    Args:

    * path: string
        The path (in terms of nested elements) to the required element.

    * root: xml.etree.ElementTree.Element
        The element from which the given path starts.

    Kwargs:

    * single_elem: boolean
        If True, this raises an error if more than one element is found. It
        also changes the return type to a single value (instead of list).

    * namespace: string or None
        The xml namespace for the given path.

    returns:
        list of strings or string (if single_elem=True)

    """
    elememts = getElements(path, root, single_elem=single_elem,
                           namespace=namespace)
    if single_elem:
        # Put single element in list so the same code can be used to do text
        # checks.
        elememts = [elememts]
    elems_text = [elem.text.strip() for elem in elememts]

    # Not all elements contain text, so this must be checked.
    no_txt_count = elems_text.count("")
    if no_txt_count != 0:
        if no_txt_count == len(elems_text):
            raise UserWarning("{path} element(s) do not contain text."\
                              .format(path=path))
        else:
            elems_text = [txt for txt in elems_text if txt != ""]
            print "Warning! This is strange, {cnt} out of {tot} {path} "\
                  "element(s) contain text (normally its all or none!)."\
                  "\nThe element(s) with no text have be removed."\
                  .format(cnt=len(elems_text) - no_txt_count,
                          tot=len(elems_text),
                          path=path)

    if single_elem:
        return elems_text[0]
    else:
        return elems_text


########## BDS XML functions ##########

def getBBox(root, namespace=xmlns):
    """
    There are two elements within the LonLatEnvelope element, the first is
    the longitude min and max, the second is the latitude. Extact this data
    and return a a list.

    Args:

    * root: xml.etree.ElementTree.Element
        The element from which the given path starts.

    Kwargs:

    * namespace: string or None
        The xml namespace for the lonLatEnvelope element.

    returns:
        list

    """
    # Assert this is a correct element somehow?
    lonLatEnvelope = getElements("lonLatEnvelope", root, single_elem=True,
                                 namespace=namespace)
    lons = lonLatEnvelope[0]
    lons = lons.text.split()
    lats = lonLatEnvelope[1]
    lats = lats.text.split()
    return [float(lons[0]), float(lats[0]),
            float(lons[1]), float(lats[1])]

def getValues(root, single_elem=False, namespace=xmlns):
    """
    Values are given under the element path "values/singleValue". Given a root
    element, extract all values and return in list.

    Args:

    * root: xml.etree.ElementTree.Element
        The element inside which the values are nested.

    Kwargs:

    * single_elem: boolean
        If True, this raises an error if more than one element is found. It
        also changes the return type to a single value (instead of list).

    * namespace: string or None
        The xml namespace for the value element.

    returns:
        list of strings or string (if single_elem=True)


    """
    return getElementsText("values/singleValue", root,
                           single_elem=single_elem, namespace=namespace)

def getAxisDescriberValues(name, root, namespace=xmlns):
    """
    Get all elements that come under the AxisDescription element;
    e.g. initialisation, forecast time, elevation.

    Args:

    * name: string
        The name of the axis describer.

    * root: xml.etree.ElementTree.Element
        The element inside which the values are nested.

    Kwargs:

    * namespace: string or None
        The xml namespace for the AxisDescription element.

    """
    axis_elems = getElements("rangeSet/RangeSet/axisDescription/"\
                             "AxisDescription",
                             root, namespace=namespace)
    for axis_elem in axis_elems:
        elem_name = getElementsText("name", root=axis_elem, single_elem=True,
                                    namespace=namespace)
        if elem_name == name:
            return getValues(axis_elem, namespace=namespace)
    return []

def check_xml(root, namespace=err_xmlns):
    """
    Check the XML is not the error response

    """
    if root.tag.strip() == namespace + "ExceptionReport":
        err_mess = getElementsText("Exception/ExceptionText", root,
                                   single_elem=True, namespace=namespace)
        raise UserWarning(err_mess)

def read_describeCoverage_xml(xml_str, namespace=xmlns):
    """
    Extract coverage information from xml (given as string) returned by
    describeCoverage request to BDS and return as Coverage object.

    Args:

    * xml_str: string
        The xml as a string.

    Kwargs:

    * namespace: string or None
        The xml namespace for the given xml_str.

    returns
        Coverage

    """
    root = ET.fromstring(xml_str)
    check_xml(root)
    # For the describeCoverage xml, only one coverage element is returned under
    # the root.
    cov_elem = getElements("CoverageOffering", root, single_elem=True,
                           namespace=namespace)

    name = getElementsText("name", cov_elem, single_elem=True,
                           namespace=namespace)
    label = getElementsText("label", cov_elem, single_elem=True,
                            namespace=namespace)
    bbox = getBBox(cov_elem, namespace=namespace)

    dim_runs = getAxisDescriberValues("DIM_RUN", cov_elem,
                                     namespace=namespace)
    dim_forecasts = getAxisDescriberValues("DIM_FORECAST", cov_elem,
                                          namespace=namespace)
    times = getAxisDescriberValues("TIME", cov_elem,
                                   namespace=namespace)
    elevations = getAxisDescriberValues("ELEVATION", cov_elem,
                                        namespace=namespace)
    CRSs = getElementsText("supportedCRSs/requestCRSs",
                           cov_elem, namespace=namespace)
    formats = getElementsText("supportedFormats/formats",
                              cov_elem, namespace=namespace)
    interpolations = getElementsText("supportedInterpolations/"\
                                     "interpolationMethod",
                                     cov_elem, namespace=namespace)

    return Coverage(name=name, label=label, bbox=bbox, dim_runs=dim_runs,
                    dim_forecasts=dim_forecasts, times=times,
                    elevations=elevations, CRSs=CRSs, formats=formats,
                    interpolations=interpolations)

def read_getCapabilities_xml(xml_str, namespace=xmlns):
    """
    Extract all coverage information from xml (given as string) returned
    by getCapabilities request to BDS and return as CoverageList object.

    Args:

    * xml_str: string
        The xml as a string.

    Kwargs:

    * namespace: string or None
        The xml namespace for the given xml_str.

    returns
        Coverage

    """
    root = ET.fromstring(xml_str)
    check_xml(root)
    cov_elems = getElements("ContentMetadata/CoverageOffering", root,
                            namespace=namespace)
    coverages = []
    for cov_elem in cov_elems:
        name = getElementsText("name", cov_elem, single_elem=True,
                               namespace=namespace)
        label = getElementsText("label", cov_elem, single_elem=True,
                                namespace=namespace)
        bbox = getBBox(cov_elem, namespace=namespace)
        coverages.append(Coverage(name=name, label=label, bbox=bbox))

    return CoverageList(coverages)
