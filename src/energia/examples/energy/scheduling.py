"""One Location, One Temporal Scale, One Operation, Linear Programming Example"""

#
# ## [Example 1]
#
# There is a single process to be optimized for cost [USD] over 4 quarters of a year.
# There is variability in terms of how much of the (known) process [Wind Farm] capacity can be accessed, and resource (Power) demand.
#


# ## Initialize

from ...components.commodity.misc import Currency
from ...components.commodity.resource import Resource
from ...components.operation.process import Process
from ...components.temporal.period import Period
from ...represent.model import Model


def scheduling():
    """A small scheduling example"""
    m = Model('scheduling')

    # ## Time
    #
    # We have 4 quarter which form a year

    m.q = Period()
    m.y = 4 * m.q

    # The horizon ($\overset{\ast}{t} = argmin_{n \in N} |\mathcal{T}_{n}|$) is determined by Energia implicitly. Check it by printing Model.Horizon

    m.horizon

    # ## Space
    #
    # If nothing is provided, a default location is created. The created single location will serve as the de facto network
    #
    # In single location case studies, it may be easier to skip providing a location all together

    m.network

    # ## Resources
    #
    # In the Resource Task Network (RTN) methodology all commodities are resources. In this case, we have a few general resources (wind, power) and a monetary resource (USD).

    m.usd = Currency()
    m.power, m.wind = Resource(), Resource()

    # ### Setting Bounds
    #
    # The first bound is set for over the network and year, given that no spatiotemporal disposition is provided:
    #
    # $\mathbf{cons}_{wind, network, year_0} \leq 400$
    #
    # For the second bound, given that a nominal is given, the list is treated as multiplicative factor. The length matches with the quarterly scale. Thus:
    #
    # $\mathbf{rlse}_{power, network, quarter_0} \geq 60$
    #
    # $\mathbf{rlse}_{power, network, quarter_1} \geq 70$
    #
    # $\mathbf{rlse}_{power, network, quarter_2} \geq 100$
    #
    # $\mathbf{rlse}_{power, network, quarter_3} \geq 30$
    #

    m.wind.consume <= 400
    m.power.release.prep(100) >= [0.6, 0.7, 1, 0.3]

    # Check the model anytime, using m.show(), or object.show()
    #
    # The first constraint is a general resource balance, generated for every resource at every spatiotemporal disposition at which an aspect regarding it is defined.
    #
    # Skip the True in .show() for a more concise set notation based print

    # ## Process

    # There are multiple ways to model this.
    #
    # Whats most important, however, is the resource balance. The resource in the brackets is the basis resource. For a negative basis, multiply the resource by the negative factor or just use negation if that applies.

    m.wf = Process()
    m.wf(m.power) == -1 * m.wind

    # Now set bounds on the extent to which the wind farm can operate. We are actually writing the following constraint:
    #
    # $\mathbf{opr} <= \phi \cdot \mathbf{cap}$
    #
    # However, we know the capacity, so it is treated as a parameter.
    #
    # Note that the incoming values are normalized by default. Use norm = False to avoid that

    m.wf.operate.prep(200, norm=False) <= [0.9, 0.8, 0.5, 0.7]

    # Add a cost to the process operation. This implies that the cost of operating is variable in every quarter. In general:
    #
    # $\dot{\mathbf{v}} == \theta \cdot \mathbf{v}$

    m.wf.operate[m.usd.spend] == [4000, 4200, 4300, 3900]

    # Note that printing can be achieved via the aspect [operate, spend, etc.] or the object

    # ## Locating the process
    #
    # The production streams are only generated once the process is places in some location. In this study, the only location is available is the default network.

    m.network.locate(m.wf)

    # Alternatively,

    # m.wf.locate(m.network)

    # # The Model
    #
    # The model consists of the following:
    #
    # 1. A general resource balances for wind in (network, year) and power in (network, quarter)
    # 2. Bounds on wind consumption [upper] and power release [lower], and wf operation [upper]
    # 3. Conversion constraints, giving produced and expended resources based on operation
    # 4. Calculation of spending USD in every quarter
    # 5. Mapping constraints for operate: q -> y and spend: q -> y (generated after objective is set)

    return m
