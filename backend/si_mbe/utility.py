from si_mbe.models import Logs


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
