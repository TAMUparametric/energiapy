from ...inputs.conversion import Conversion
from ...type.component.process import ProcessType


def conversioner(process):
    """updates conversion to Conversion

    Args:
        process: energiapy Process
    """

    if not isinstance(process.conversion, Conversion):
        process.conversion = Conversion(
            conversion=process.conversion, process=process)
        # conversion can be single mode (SINGLE_PRODMODE) or multimode (MULTI_PRODMODE)
        # For MULTI_PRODMODE, a dict of type {'mode' (str, int) : {Resource:
        # float}} needs to be provided
        for i in ['modes', 'n_modes', 'balance', 'involve']:
            setattr(process, i, getattr(process.conversion, i))

        if process.n_modes > 1:
            process.ctypes.append(ProcessType.MULTI_PRODMODE)
        elif process.n_modes == 1:
            process.ctypes.append(ProcessType.SINGLE_PRODMODE)

        if process.produce is not None:
            setattr(
                process,
                'produce',
                {getattr(process.conversion, 'produce'): process.produce},
            )
        else:
            setattr(
                process, 'produce', {
                    getattr(
                        process.conversion, 'produce'): 1})

        for i in ['discharge', 'consume']:
            if getattr(process, i) is not None:
                if isinstance(getattr(process, i), dict):
                    dict_ = getattr(process, i)
                    setattr(
                        process,
                        i,
                        {r: dict_.get(r, True) for r in getattr(process.conversion, i)},
                    )  # if defined outside and is a dictionary. Add True the ones not mentioned
                else:
                    raise ValueError(
                        f'{process}.{i} should be provided as a dictionary'
                    )
            else:
                setattr(
                    process, i, {
                        r: True for r in getattr(
                            process.conversion, i)})
