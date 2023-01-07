from si_mbe.models import Logs
from datetime import date
from calendar import monthrange


def perform_log(request: any, operation: str, table: str) -> None:
    Logs.objects.create(
        user_id=request.user,
        operation=operation,
        table=table,
    )


def sales_adjust_sparepart_quantity(
                                    new_instance: any = None,
                                    old_instance: any = None,
                                    old_data_list: list = [],
                                    create: bool = False,
                                    update: bool = False
                                ) -> None:
    '''
    A function to adjust sparepart quantity after Creating, Updating, and Deleting
    Sales data / object / instance
    '''
    instance = new_instance
    old_sales_details = old_instance

    if create:
        # Subtracting spareapart quantity with new sales detail data
        for sales_detail in instance.sales_detail_set.all():
            # Get the Sparepart instance associated with the Sales_detail instance
            sparepart = sales_detail.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= sales_detail.quantity
            sparepart.save()
    elif update:
        # looping trought new sales_detail data to adjust sparepart quantity
        for sales_detail in instance.sales_detail_set.all():
            # Get the Sparepart instance associated with the sales_detail instance
            sparepart = sales_detail.sparepart_id

            # Find the old sales_detail instance with the same sparepart_id
            old_sales_detail = next(
                (sd for sd in old_sales_details if sd.sparepart_id == sparepart),
                None
            )

            # Update the quantity field of the Sparepart instance:
            # 1. If an old sales_detail instance was found, increase the quantity field of
            # the Sparepart instance by the old quantity value
            if old_sales_detail:
                sparepart.quantity += old_sales_detail.quantity

            # 2. Decrease the quantity field of the Sparepart instance by the new quantity value
            sparepart.quantity -= sales_detail.quantity
            sparepart.save()

        # Loop over all the old sales_detail instances
        for old_sales_detail in old_sales_details:
            # Check if the old sales_detail instance is not present in the
            # new data / updated instance
            if old_sales_detail not in instance.sales_detail_set.all():
                sparepart = old_sales_detail.sparepart_id
                # increase the quantity field of the Sparepart instance by the old
                # quantity value
                sparepart.quantity += old_sales_detail.quantity
                sparepart.save()
    else:
        # Adding (plus) Sparepart quantity with old sales detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Sales_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += old_data['quantity']
            sparepart.save()


def restock_adjust_sparepart_quantity(
                                    new_instance: any = None,
                                    old_instance: any = None,
                                    old_data_list: list = [],
                                    create: bool = False,
                                    update: bool = False
                                ) -> None:
    '''
    A function to adjust sparepart quantity after Creating, Updating, and Deleting
    Restock data / object / instance
    '''
    instance = new_instance
    old_restock_details = old_instance

    if create:
        # Subtracting spareapart quantity with new restock detail data
        for restock_detail in instance.restock_detail_set.all():
            # Get the Sparepart instance associated with the Restock_detail instance
            sparepart = restock_detail.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += restock_detail.quantity
            sparepart.save()
    elif update:
        # looping trought new restock sparepart data to adjust sparepart quantity
        for restock_detail in instance.restock_detail_set.all():
            # Get the Sparepart instance associated with the restock_detail instance
            sparepart = restock_detail.sparepart_id

            # Find the old restock_sparepart instance with the same sparepart_id
            old_restock_detail = next(
                (rd for rd in old_restock_details if rd.sparepart_id == sparepart),
                None
            )

            # Update the quantity field of the Sparepart instance:
            # 1. If an old restock_detail instance was found, increase the quantity field of
            # the Sparepart instance by the old quantity value
            if old_restock_detail:
                sparepart.quantity -= old_restock_detail.quantity

            # 2. Decrease the quantity field of the Sparepart instance by the new quantity value
            sparepart.quantity += restock_detail.quantity
            sparepart.save()

        # Loop over all the old restock_detail instances, to find old but not present data in new data
        for old_restock_detail in old_restock_details:
            # Check if the old Service_sparepart instance is not present in the
            # new data / updated instance
            if old_restock_detail not in instance.restock_detail_set.all():
                sparepart = old_restock_detail.sparepart_id
                # increase the quantity field of the Sparepart instance by the old
                # quantity value
                sparepart.quantity -= old_restock_detail.quantity
                sparepart.save()
    else:
        # Adding (plus) Sparepart quantity with old restock detail data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old Restock_detail instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= old_data['quantity']
            sparepart.save()


def service_adjust_sparepart_quantity(
                                    new_instance: any = None,
                                    old_instance: any = None,
                                    old_data_list: list = [],
                                    create: bool = False,
                                    update: bool = False
                                ) -> None:
    '''
    A function to adjust sparepart quantity after Creating, Updating, and Deleting
    Service data / object / instance
    '''
    instance = new_instance
    old_service_spareparts = old_instance

    if create:
        # Subtracting spareapart quantity with new service_sparepart data
        for service_sparepart in instance.service_sparepart_set.all():
            # Get the Sparepart instance associated with the Service_sparepart instance
            sparepart = service_sparepart.sparepart_id
            # Update the quantity field of the Sparepart instance
            sparepart.quantity -= service_sparepart.quantity
            sparepart.save()
    elif update:
        # looping trought new service sparepart data to adjust sparepart quantity
        for service_sparepart in instance.service_sparepart_set.all():
            # Get the Sparepart instance associated with the Service_sparepart instance
            sparepart = service_sparepart.sparepart_id

            # Find the old Service_sparepart instance with the same sparepart_id
            old_service_sparepart = next(
                (ss for ss in old_service_spareparts if ss.sparepart_id == sparepart),
                None
            )

            # Update the quantity field of the Sparepart instance:
            # 1. If an old Service_action instance was found, increase the quantity field of
            # the Sparepart instance by the old quantity value
            if old_service_sparepart:
                sparepart.quantity += old_service_sparepart.quantity

            # 2. Decrease the quantity field of the Sparepart instance by the new quantity value
            sparepart.quantity -= service_sparepart.quantity
            sparepart.save()

        # Loop over all the old Service_sparepart instances
        for old_service_sparepart in old_service_spareparts:
            # Check if the old Service_sparepart instance is not present in the
            # new data / updated instance
            if old_service_sparepart not in instance.service_sparepart_set.all():
                sparepart = old_service_sparepart.sparepart_id
                # increase the quantity field of the Sparepart instance by the old
                # quantity value
                sparepart.quantity += old_service_sparepart.quantity
                sparepart.save()
    else:
        # Adding (plus) Sparepart quantity with old service_sparepart data
        for old_data in old_data_list:
            # Get the Sparepart instance associated with the old service_sparepart instance
            sparepart = old_data['sparepart_id']
            # Update the quantity field of the Sparepart instance
            sparepart.quantity += old_data['quantity']
            sparepart.save()


def get_sales_report(
                    data_list: list,
                    year: int = date.today().year,
                    month: int = date.today().month,
                ) -> dict:
    '''
    Function to get sales report information per day as dict (date, sales_transaction, sales_revenue, sales_count),
    total sales a month, total revenue a month.

    Then return a dict as result in format of {sales_report, sales_transaction_month, sales_revenue_month}
    '''
    # Getting number of day form current month
    number_of_day = monthrange(year=year, month=month)[1]

    # Getting total revenue per day in particular a month
    sales_report = []

    # Getting sales revenue, transaction, and count for a month
    sales_transaction_month = 0
    sales_revenue_month = 0

    data_list = data_list

    # Make sales report information in particular month
    for i, object in enumerate(range(number_of_day), 1):
        # Getting sales revenue, transaction, and count for a day
        sales_transaction = 0
        sales_revenue = 0
        sales_count = 0

        for sales in data_list:
            if sales['created_at'] == date(year, month, i).strftime('%d-%m-%Y'):
                sales_transaction_month += sales['total_price_sales']
                sales_revenue_month += int(sales['deposit'])
                sales_transaction += sales['total_price_sales']
                sales_revenue += int(sales['deposit'])
                sales_count += 1
        sales_report.append({
            'date': date(year, month, i),
            'sales_transaction': sales_transaction,
            'sales_revenue': sales_revenue,
            'sales_count': sales_count
        })

    return {
                'sales_report': sales_report,
                'sales_transaction_month': sales_transaction_month,
                'sales_revenue_month': sales_revenue_month
            }


def get_restock_report(
                    data_list: list,
                    year: int = date.today().year,
                    month: int = date.today().month,
                ) -> dict:
    '''
    Function to get restock report information per day as dict (date, restock_transaction, restock_cost),
    total restock a month, total revenue a month.

    Then return a dict as result in format of {restock_report, restock_transaction_month, restock_cost_month}
    '''
    # Getting number of day form current month
    number_of_day = monthrange(year=year, month=month)[1]

    # Getting restock report information per day in particular a month
    restock_report = []

    # Getting restock cost and transaction for a month
    restock_transaction_month = 0
    restock_cost_month = 0

    data_list = data_list

    # Make restock report information in particular month
    for i, object in enumerate(range(number_of_day), 1):
        # Getting restock cost and transaction for a day
        restock_transaction = 0
        restock_cost = 0

        for restock in data_list:
            if restock['created_at'] == date(year, month, i).strftime('%d-%m-%Y'):
                restock_transaction_month += restock['total_restock_cost']
                restock_cost_month += int(restock['deposit'])
                restock_transaction += restock['total_restock_cost']
                restock_cost += int(restock['deposit'])
        restock_report.append({
            'date': date(year, month, i),
            'restock_transaction': restock_transaction,
            'restock_cost': restock_cost,
        })

    return {
                'restock_report': restock_report,
                'restock_transaction_month': restock_transaction_month,
                'restock_cost_month': restock_cost_month
            }


def get_service_report(
                    data_list: list,
                    year: int = date.today().year,
                    month: int = date.today().month,
                ) -> dict:
    '''
    Function to get service report information per day as dict (date, service_transaction, service_revenue),
    total service a month, total revenue a month.

    Then return a dict as result in format of {service_report, service_transaction_month, service_revenue_month}
    '''
    # Getting number of day form current month
    number_of_day = monthrange(year=year, month=month)[1]

    # Getting service report information per day in particular a month
    service_report = []

    # Getting service revenue and transaction for a month
    service_transaction_month = 0
    service_revenue_month = 0

    data_list = data_list

    # Make service report information in particular month
    for i, object in enumerate(range(number_of_day), 1):
        # Getting service revenue and transaction for a day
        service_transaction = 0
        service_revenue = 0

        for service in data_list:
            if service['created_at'] == date(year, month, i).strftime('%d-%m-%Y'):
                service_transaction_month += service['total_service_price']
                service_revenue_month += int(service['deposit'])
                service_transaction += service['total_service_price']
                service_revenue += int(service['deposit'])
        service_report.append({
            'date': date(year, month, i),
            'service_transaction': service_transaction,
            'service_revenue': service_revenue,
        })

    return {
                'service_report': service_report,
                'service_transaction_month': service_transaction_month,
                'service_revenue_month': service_revenue_month
            }
