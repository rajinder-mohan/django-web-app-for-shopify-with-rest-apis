from .models import Account
from table import Table
from table.columns import Column
from django.core.urlresolvers import reverse_lazy


class AccountTable(Table):
	id = Column(field='id')
	first_name = Column(field='first_name')
	last_name = Column(field='last_name')
	emailid = Column(field='emailid')

	class Meta:
		model = Account
		# ajax = True
		# ajax_source = reverse_lazy('table_data')
