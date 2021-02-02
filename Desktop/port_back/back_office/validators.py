from decimal import Decimal

from rest_framework.exceptions import ValidationError


class CheckDedweightList:
    """
    Checking input deadweight
    """
    requires_context = True
    min_gap = '1'

    def __call__(self, value, serializer_field):
        """
        Checks that deadweight list:
            - did not intersect
            - the first one started from scratch
            - the last one ended with None
            - the distance between deadweight should not be less than self.min_gap
        """
        deadweight_prices = value.get('prices')
        deadweights = [(deadweight.get('from_deadweight'), deadweight.get('to_deadweight'))
                       for deadweight in deadweight_prices]
        deadweights = sorted(deadweights, key=lambda item: item[0])
        if deadweights[0][0] != 0:
            raise ValidationError('The initial deadweight must be 0')
        if deadweights[-1][-1] is not None:
            raise ValidationError('The last deadweight must be null')
        if len(deadweights) == 1:
            return True
        for i in range(len(deadweights) - 1):
            if not deadweights[i][1]:
                raise ValidationError('Only the last deadweight must be null')
            if deadweights[i][1] >= deadweights[i + 1][0]:
                raise ValidationError('Deadweights should not overlap')
            if Decimal(str(deadweights[i + 1][0])) - Decimal(str(deadweights[i][1])) > Decimal(self.min_gap):
                raise ValidationError(f'There should be no gaps greater than {self.min_gap} between the deadweights')
