from itcs import magic_numbers
from personal_cabinet.core import SailorGetQuerySetMixin


class ETransportSailorGetQuerySetMixin(SailorGetQuerySetMixin):
    """
    Document statuses that are not available for viewing in the morrichservice account
    """

    def get_exclude_status_document(self):
        return (
            magic_numbers.STATUS_REMOVED_DOCUMENT,
            magic_numbers.STATUS_CREATED_BY_AGENT,
            magic_numbers.CREATED_FROM_MORRICHSERVICE,
            magic_numbers.status_statement_canceled,
            magic_numbers.status_state_qual_dkk_canceled,
            magic_numbers.SQC_WAIT_DECISION,
            magic_numbers.SQC_WAIT_SIGNATURES,
        )
