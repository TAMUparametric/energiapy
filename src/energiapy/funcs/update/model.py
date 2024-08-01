def update_element(self, value: Dict[IsScale, IsInput]: component: IsComponent, aspect: IsAspect, horizon: IsHorizon, bound: Bound, certainty: Certainty, approach: Approach):
    for scale_, value_ in value.items():
        for i, j in enumerate(list(value_)):
            for rule in rulebook.find(aspect):
                parameter_, associated_, bound_ = (None for _ in range(3))

                parameter = Parameter(value=j, aspect=aspect, component=component, declared_at=declared_at, horizon=horizon,
                                      bound=bound[i], certainty=certainty[i], approach=approach[i], temporal=scale_)

                variable = Variable(aspect=aspect, component=component,
                                    declared_at=declared_at, temporal=parameter.temporal)

                self.parameters = sorted(
                    set(self.parameters) | {parameter})
                self.variables = sorted(set(self.variables) | {variable})

                if rule.associated:
                    associated_ = Variable(
                        aspect=rule.associated, component=component, declared_at=declared_at, temporal=parameter.temporal)

                if rule.parameter:
                    parameter_ = parameter

                if is_(rule.condition, Condition.BIND):
                    bound_ = parameter.bound
                if rule.declared_at and is_not(declared_at.cname(), rule.declared_at):
                    continue
                else:
                    constraint = Constraint(condition=rule.condition, variable=variable,
                                            associated=associated_, declared_at=declared_at, parameter=parameter_, bound=bound_, rhs=rule.rhs)
                    self.constraints = sorted(
                        set(self.constraints) | {constraint})
