from ..model.specialparams.conversion import Conversion

from ..components.type.process import ProcessType


def conversioner(process):
    """updates conversion to Conversion

    Args:
        process: energiapy Process

    """

    if not isinstance(process.conversion, Conversion):
        process.conversion = Conversion(
            conversion=process.conversion, process=process)
        # conversion can be single mode (SINGLE_PRODMODE) or multimode (MULTI_PRODMODE)
        # For MULTI_PRODMODE, a dict of type {'mode' (str, int) : {Resource: float}} needs to be provided
        for i in ['modes', 'n_modes', 'balance', 'involve']:
            setattr(process, i, getattr(process.conversion, i))

        if process.n_modes > 1:
            process.ctype.append(ProcessType.MULTI_PRODMODE)
        elif process.n_modes == 1:
            process.ctype.append(ProcessType.SINGLE_PRODMODE)

        # setattr(process, 'produce', getattr(process.conversion, 'base'))

        for i in ['discharge', 'consume', 'produce']:
            set_to = True
            if i == 'produce':
                set_to = 1

            print(getattr(process, i))

            if getattr(process, i) and isinstance(getattr(process, i), dict):
                dict_ = getattr(process, i)
                setattr(process, i, {r: dict_.get(r, set_to)
                        for r in getattr(process.conversion, i)})  # if defined outside and is a dictionary. Add True the ones not mentioned
                print(getattr(process, i))

            elif not getattr(process, i):
                setattr(
                    process, i, {r: set_to for r in getattr(process.conversion, i)})

            else:
                raise ValueError(
                    f'{i} should be either IsValue or Dict[Resource, IsValue]')
