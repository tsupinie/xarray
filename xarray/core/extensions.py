from .dataarray import DataArray
from .dataset import Dataset


class AccessorRegistrationError(Exception):
    """Exception for conflicts in accessor registration."""


class _CachedAccessor(object):
    """Custom property-like object (descriptor) for caching accessors."""
    def __init__(self, name, accessor):
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        if obj is None:
            # we're accessing the attribute of the class, i.e., Dataset.geo
            return self._accessor
        accessor_obj = self._accessor(obj)
        # Replace the property with the accessor object. Inspired by:
        # http://www.pydanny.com/cached-property.html
        # We need to use object.__setattr__ because we overwrite __setattr__ on
        # AttrAccessMixin.
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj


def _register_accessor(name, cls):
    def decorator(accessor):
        if hasattr(cls, name):
            raise AccessorRegistrationError(
                'cannot register accessor %r under name %r for type %r '
                'because an attribute with that name already exists.'
                % (accessor, name, cls))
        setattr(cls, name, _CachedAccessor(name, accessor))
        return accessor
    return decorator


def register_dataarray_accessor(name):
    """Register a custom accessor on xarray.DataArray objects.

    Parameters
    ----------
    name : str
        Name under which the accessor should be registered.

    Examples
    --------

    In your library code::

        import xarray as xr

        @xr.register_dataset_accessor('geo')
        class GeoAccessor(object):
            def __init__(self, xarray_obj):
                self._obj = xarray_obj

            @property
            def center(self):
                # return the geographic center point of this dataset
                lon = self._obj.latitude
                lat = self._obj.longitude
                return (float(lon.mean()), float(lat.mean()))

            def plot(self):
                # plot this array's data on a map, e.g., using Cartopy
                pass

    Back in an interactive IPython session:

        >>> ds = xarray.Dataset({'longitude': np.linspace(0, 10),
        ...                      'latitude': np.linspace(0, 20)})
        >>> ds.geo.center
        (5.0, 10.0)
        >>> ds.geo.plot()
        # plots data on a map

    See also
    --------
    xarray.register_dataset_accessor
    """
    return _register_accessor(name, DataArray)


def register_dataset_accessor(name):
    """Register a custom property on xarray.Dataset objects.

    Parameters
    ----------
    name : str
        Name under which the property should be registered.

    See also
    --------
    xarray.register_dataarray_accessor
    """
    return _register_accessor(name, Dataset)
