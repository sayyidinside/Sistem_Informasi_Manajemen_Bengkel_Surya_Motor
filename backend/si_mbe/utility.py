from calendar import monthrange
from datetime import date
from io import BytesIO
import locale
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, TableStyle
from reportlab.lib.styles import ParagraphStyle
from si_mbe.models import Logs
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from rest_framework.exceptions import ValidationError


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


def format_money(number: int) -> str:
    # formating number to include . after three number
    locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
    formatted_number = locale.format_string("%d", number, grouping=True)
    money = f'{formatted_number},00'

    return money


def generate_report_pdf(
                    data: dict,
                    report_type: str,
                    year: int = date.today().year,
                    month: int = date.today().month
                ):
    '''
    A function to generate pdf file using user input data.

    This function takes few arguments:
    - data (required) as main ingredients to create pdf content;
    - report_type (required) to create filename, title, and few operation in creating pdf file;
    - year (additional) to create filename and subtitle, when not given use current year;
    - month (additional) to create filename and subtitle, when not given use current month.
    '''
    # Setting up data and non_table_data as blank dict
    data = data
    non_table_data = {}

    # Checking report_type value, then assinging non table data and data based on report_type
    if report_type == 'Penjualan':
        non_table_data['transaction_month'] = data.pop('sales_transaction_month')
        non_table_data['revenue_month'] = data.pop('sales_revenue_month')
        data = data['sales_report']
        column_2 = 'sales_transaction'
        column_3 = 'sales_revenue'
    elif report_type == 'Pengadaan':
        non_table_data['transaction_month'] = data.pop('restock_transaction_month')
        non_table_data['cost_month'] = data.pop('restock_cost_month')
        data = data['restock_report']
        column_2 = 'restock_transaction'
        column_3 = 'restock_cost'
    elif report_type == 'Servis' or report_type == 'Service':
        non_table_data['transaction_month'] = data.pop('service_transaction_month')
        non_table_data['revenue_month'] = data.pop('service_revenue_month')
        data = data['service_report']
        column_2 = 'service_transaction'
        column_3 = 'service_revenue'
    else:
        raise ValidationError('Report Type Input Is Incorrect')

    buffer = BytesIO()

    # Create a new PDF document with an A4 size page
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.0*cm, rightMargin=1.0*cm,
                            topMargin=0.9*cm, bottomMargin=1.5*cm
                            )

    # Extract the keys from the first dictionary to use as column headings
    keys = data[0].keys()

    # Create a style for the title
    styles = getSampleStyleSheet()
    title_style = styles['Title']

    # Crate a style for subtitle
    sub_title_style = ParagraphStyle(
        name='sub_title',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=16,
        alignment=TA_CENTER
    )

    # Create the title and sub title with their own resprective style
    title = Paragraph(f'Laporan {report_type} Bengkel Mulya Motor', title_style)
    sub_title = Paragraph(f'Periode = {year} - {month}', style=sub_title_style)

    # Create a list of lists with the data for each cell by transforming data dict
    table_data = []
    for row in data:
        temp_list = []
        for key in keys:
            if key == column_2 or key == column_3:
                money = format_money(row[key])
                temp_list.append(money)
            else:
                temp_list.append(row[key])
        table_data.append(temp_list)

    # Setting up table heading and footing
    if report_type == 'Penjualan':
        table_data.insert(0, ['Tanggal', 'Transaksi\n(Rp)', 'Pembayaran\n(Rp)', 'Jumlah'])
        table_data.append([
            f'Total {report_type}',
            format_money(non_table_data["transaction_month"]),
            format_money(non_table_data["revenue_month"]),
            ''
        ])
    else:
        table_data.insert(0, ['Tanggal', 'Transaksi\n(Rp)', 'Biaya\n(Rp)'])
        if report_type == 'Pengadaan':
            table_data.append([
                f'Total {report_type}',
                format_money(non_table_data["transaction_month"]),
                format_money(non_table_data["cost_month"])
            ])
        else:
            table_data.append([
                f'Total {report_type}',
                format_money(non_table_data["transaction_month"]),
                format_money(non_table_data["revenue_month"])
            ])

    # Create the table with custome width
    table = Table(table_data, colWidths=[110, 125, 125, 80])

    # Create table_style
    table_style = TableStyle([
        # Setting up style for table heading
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('LEADING', (1, 0), (2, 0), 15),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BOX', (0, 0), (-1, 0), 1, colors.black),

        # Setting up style for table content
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
        ('LEFTPADDING', (1, 1), (2, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, int(len(table_data)-2)), (-1, int(len(table_data)-2)), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, int(len(table_data)-2)), [colors.lightgrey, colors.whitesmoke]),

        # Setting up style for table footing
        ('BACKGROUND', (0, -1), (-1, -1), colors.gray),
        ('TOPPADDING', (0, -1), (-1, -1), 0),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 5),
        ('BOX', (0, -1), (-1, -1), 1, colors.black),

        # Setting up borders for table
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('BOX', (0, 0), (0, -1), 0.5, colors.black),
        ('BOX', (1, 0), (1, -1), 0.5, colors.black),
        ('BOX', (2, 0), (2, -1), 0.5, colors.black),
    ])

    if report_type == 'Penjualan':
        table_style.add('ALIGN', (-1, 1), (-1, -1), 'CENTER')
        table_style.add('BOX', (3, 0), (3, -1), 0.5, colors.black)

    # Set the style for the first row (the column headings)
    table.setStyle(table_style)

    # Create a space between the table and the additional information
    space = Spacer(1, 25)

    # Add the table to the PDF document
    doc.build([title, sub_title, space, table])

    buffer.seek(0)

    # Send builded pdf file to user
    response = FileResponse(buffer, as_attachment=True, filename=f'Laporan_{report_type}-{year}-{month}.pdf')

    return response


def generate_receipt(
                    data: dict,
                    transaction_type: str,
                ):
    '''
    A function to generate transaction receipt to print using user input data.

    This function takes few arguments:
    - data (required) as main ingredients to create reciept content;
    - transaction_type (required) to create filename, title, and few operation in creating reciept
    '''
    # print(data)
    if transaction_type in ('Penjualan', 'Sales'):
        keyword = ('Sales', 'sales')

        # Retrieve transation_detail list from main transaction
        content = data.pop('content', [])

        # Retrieve items count to make dynamic paper lenght
        item_count = len(content) * 2
        height = (67 + (item_count*4))*mm

        # Creating table from the content of transaction for sales
        content_list = [['Qty', 'Harga', 'Jumlah']]
        for item in content:
            temp_list = []
            for info in item:
                if info == 'sparepart':
                    content_list.append([item[info]])
                elif info == 'quantity':
                    temp_list.append(item[info])
                elif info in ('individual_price', 'sub_total'):
                    money = format_money(item[info])
                    temp_list.append(money)
            content_list.append(temp_list)
    else:
        keyword = ('Service', 'service')

        # Retrieve transation_detail list from main transaction
        content_sparepart = data.pop('service_spareparts', [])
        content_action = data.pop('service_actions', [])

        action_count = len(content_action)
        sparepart_count = (len(content_sparepart) * 2)

        # Retrieve items count to make dynamic paper lenght
        item_count = action_count + sparepart_count
        height = (77 + (item_count*4))*mm

        # Creating table from the content of transaction for sales
        content_list = [['Qty', 'Harga', 'Jumlah']]
        for sparepart in content_sparepart:
            temp_list = []
            for info in sparepart:
                if info == 'sparepart':
                    content_list.append([sparepart[info]])
                elif info == 'quantity':
                    temp_list.append(sparepart[info])
                elif info in ('individual_price', 'sub_total'):
                    money = format_money(int(sparepart[info]))
                    temp_list.append(money)
            content_list.append(temp_list)
        for action in content_action:
            temp_list = []
            for info in action:
                if info == 'name':
                    temp_list.append(action[info])
                    temp_list.append(None)
                if info == 'cost':
                    temp_list.append(format_money(int(action[info])))
            content_list.append(temp_list)

    # Creating table for customer information
    customer_list = []
    customer_list.append(['Pelanggan', f': {data["customer_name"]}'])
    if transaction_type not in ('Penjualan', 'Sales'):
        customer_list.append(['Jenis Motor', f': {data["motor_type"]}'])
        customer_list.append(['No Polisi', f': {data["police_number"]}'])

    # Adding payment information to table
    if transaction_type in ('Penjualan', 'Sales'):
        content_list.append([None, 'Total Item', data['total_quantity']])
        content_list.append([None, 'Sub Total', format_money(data['total_price'])])
        content_list.append([None, 'Discount', format_money(int(data['discount']))])
        content_list.append([None, 'Total', format_money(data['final_total_price'])])
    else:
        content_list.append([data['total_quantity'], 'Sub Total Part', format_money(data['sub_total_part'])])
        content_list.append([None, 'Sub Total Jasa', format_money(data['sub_total_action'])])
        content_list.append([None, 'Sub Total', format_money(data['total_price'])])
        content_list.append([None, 'Discount', format_money(int(data['discount']))])
        content_list.append([None, 'Total', format_money(data['final_total_price'])])

    content_list.append([None, 'Tunai', format_money(int(data['deposit']))])
    if data['remaining_payment'] == 0:
        content_list.append([None, 'Kembalian', format_money(data['change'])])
    else:
        content_list.append([None, 'Sisa', format_money(data['remaining_payment'])])

    # Create the table for customer information with custome width
    customer_table = Table(customer_list, colWidths=[11.5*mm, 11*mm], rowHeights=3*mm, hAlign='LEFT')

    # Create the table for service contents with custome width
    content_table = Table(content_list, colWidths=[14*mm, 18.75*mm, 18.75*mm], rowHeights=4*mm)

    # Create style for customer information table
    customer_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # Create style for content table
    content_table_style = TableStyle([
        # Setting up style for table heading
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black, None, (1.95, 0.45)),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black, None, (1.95, 0.45)),
        ('LEADING', (0, 0), (-1, 0), 7.7),

        # Setting up style for table content
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEADING', (0, 1), (-1, -2), 4),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('LEADING', (0, -1), (-1, -1), 6.5),
        ('BOTTOMPADDING', (0, 1), (-1, item_count), 6),

        # Setting up style for payment info
        ('ALIGN', (1, item_count+1), (1, -1), 'LEFT'),
        ('LEFTPADDING', (1, item_count+1), (1, -1), 10),
        ('LINEABOVE', (0, item_count+1), (-1, item_count+1), 0.5, colors.black, None, (1.95, 0.45)),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black, None, (1.95, 0.45)),
    ])

    # check in it's service transaction adding few style to table
    if transaction_type not in ('Penjualan', 'Sales'):
        content_table_style.add('LINEABOVE', (0, sparepart_count+1), (-1, sparepart_count+1),
                                0.5, colors.black, None, (1.95, 0.45))

    # Set the stle for customer table
    customer_table.setStyle(customer_table_style)

    # Set the style for the content table
    content_table.setStyle(content_table_style)

    # Create receipt template
    receipt = []

    # Adding reciept data
    receipt.append(Paragraph('Bengkel Mulya Motor',
                   style=ParagraphStyle(name='title', fontSize=10, alignment=TA_CENTER, leading=15)))
    receipt.append(Paragraph('Roku Taman Alamanda II Blok EB 1A No.14&16, Mustikasari - Mustika Jaya, Bekasi Timur',
                   style=ParagraphStyle(name='address', fontSize=6, alignment=TA_CENTER, leading=7)))
    receipt.append(Paragraph('No.Telp. 0812 1906 8313 - 0878 8090 5501',
                   style=ParagraphStyle(name='address', fontSize=6, alignment=TA_CENTER, leading=7)))
    receipt.append(Paragraph('WA. 0895 3561 94945',
                   style=ParagraphStyle(name='address', fontSize=6, alignment=TA_CENTER, leading=7)))
    receipt.append(Spacer(0, 5))
    receipt.append(customer_table)
    receipt.append(Paragraph(f'#{data[f"{keyword[1]}_id"]} - {data["created_at"]}',
                   style=ParagraphStyle(name='receipt_info', fontSize=6, leading=10, leftIndent=6)))
    receipt.append(content_table)
    receipt.append(Spacer(0, 3))
    receipt.append(Paragraph('Terima Kasih Telah Bertransaksi di Bengkel Mulya Motor',
                   style=ParagraphStyle(name='footer', fontSize=5, alignment=TA_CENTER, leading=0)))

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=(57*mm, height),
                            leftMargin=0.06*cm, rightMargin=0.06*cm,
                            topMargin=0.5*cm, bottomMargin=0.015*cm
                            )

    doc.build(receipt)

    buffer.seek(0)

    # Send builded pdf file to user
    response = FileResponse(
        buffer,
        as_attachment=False,
        filename=f'{keyword[0]}_Receipt_{data[f"{keyword[1]}_id"]}.pdf'
    )

    return response
