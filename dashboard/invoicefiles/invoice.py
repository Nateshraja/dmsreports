from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from datetime import date, datetime,timedelta
from dashboard import views

def sales_invoice(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/invoice/sales_invoice.html', context)


def sales_invoice_report(request):
    # Retrieve parameters
    code = request.session.get('param1')
    type_param = request.session.get('param2')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    division = request.GET.get('division')
    group1 = request.GET.get('group1')
    distributor = request.GET.get('distributor')

    # Default date range
    if not from_date:
        from_date = (datetime.now().replace(day=1) - timedelta(days=30)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    if type_param == 'Ramraj':
        try:
            # Build dynamic query
            query = """SELECT state_code, distributor_code, distributor_name, cmp_dis_per, invno, invoice_date, cus_name, cardcode,
division, group1, group2, rr_item, prod_category category, product_name, product_variant_name, inv_qty, inv_untax_amt, 
inv_amt, schemeqty, price_unit, frate, scheme_untax_amt, scheme_amt, ret_qty, ret_price_unit, ret_frate, 
ret_untax_amt, ret__amt, ret_schemeqty, ret_scheme_price_unit, ret_scheme_frate, ret_scheme_untax_amt, ret_scheme_amt
FROM public."Monthly_Divisionwise_Sales_Report" where 1=1"""
            filters = []

            if division:
                query += " AND division = %s"
                filters.append(division)
            if group1:
                query += " AND group1 = %s"
                filters.append(group1)
            if distributor:
                query += " AND distributor_name ILIKE %s"
                filters.append(f"%{distributor}%")
            query += " AND invoice_date BETWEEN %s AND %s"
            filters.extend([from_date, to_date])
            #print(filters)
            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query, filters)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert rows to JSON format
            data = [
                {col_name: (value.strftime('%d-%m-%Y') if isinstance(value, (datetime, date)) else value)
                 for col_name, value in zip(columns, row)}
                for row in rows
            ]

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    if type_param=='Distributor':
        try:
            # Build dynamic query
            query = """SELECT state_code, distributor_code, distributor_name, cmp_dis_per, invno, invoice_date, cus_name, cardcode,
division, group1, group2, rr_item, prod_category category, product_name, product_variant_name, inv_qty, inv_untax_amt, 
inv_amt, schemeqty, price_unit, frate, scheme_untax_amt, scheme_amt, ret_qty, ret_price_unit, ret_frate, 
ret_untax_amt, ret__amt, ret_schemeqty, ret_scheme_price_unit, ret_scheme_frate, ret_scheme_untax_amt, ret_scheme_amt
FROM public."Monthly_Divisionwise_Sales_Report" WHERE distributor_code = %s"""
            filters = [code]
            if division:
                query += " AND division = %s"
                filters.append(division)
            if group1:
                query += " AND group1 = %s"
                filters.append(group1)
            if distributor:
                query += " AND distributor_name ILIKE %s"
                filters.append(f"%{distributor}%")
            query += " AND invoice_date BETWEEN %s AND %s"
            filters.extend([from_date, to_date])
            print(filters)
            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query, filters)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert rows to JSON format
            data = [
                {col_name: (value.strftime('%d-%m-%Y') if isinstance(value, (datetime, date)) else value)
                 for col_name, value in zip(columns, row)}
                for row in rows
            ]

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


'''
def sales_invoice_report(request):
    # Retrieve parameters from session
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    #print("Code:", code)
    #print("Type Param:", type_param)

    from_date = request.GET.get('from_date')  # Get 'from_date' from request
    to_date = request.GET.get('to_date')      # Get 'to_date' from request

    # Set default date range if not provided
    if not from_date:
        from_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')  # Start of current month
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')  # Today's date

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)

    if type_param == 'Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT docentry, discount, walkin_name, walkin_phone, walkin_addr, invno, 
                    invoice_user_id, division, brand, state_code, distributor_code, distributor_name,
                    "name", rr_item, "ref", yearsales, yearqty, invoice_date, vp_products, group1, group2, prod_category
                    FROM public."sales_invoice_BI" """)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert rows to JSON format, handling datetime serialization
            data = []
            for row in rows:
                row_data = {}
                for col_name, value in zip(columns, row):
                    # Convert datetime fields to "day-month-year" format
                    if isinstance(value, (date, datetime)):
                        row_data[col_name] = value.strftime('%d-%m-%Y')
                    else:
                        row_data[col_name] = value
                data.append(row_data)

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT docentry, discount, walkin_name, walkin_phone, walkin_addr, invno, 
invoice_user_id, division, brand, state_code, distributor_code, distributor_name,
"name", rr_item, "ref", yearsales, yearqty, invoice_date, vp_products, group1, group2, prod_category
FROM public."sales_invoice_BI"   where distributor_code = %s""", [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            data = []
            for row in rows:
                row_data = {}
                for col_name, value in zip(columns, row):
                    # Convert datetime fields to "day-month-year" format
                    if isinstance(value, (date, datetime)):
                        row_data[col_name] = value.strftime('%d-%m-%Y')
                    else:
                        row_data[col_name] = value
                data.append(row_data)

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
'''


def sales_return(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/invoice/sales_return.html', context)


def sales_return_report(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    print(code)
    print(type_param)

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rc.state_code,
    rc.distributor_code AS dbrcode,
    rc.name AS distributor_name,
    cd.company_id AS division,
    br.name AS brand,
    pc.name AS category,
    pp.id AS product_id,
    pp.product_variant_name,
    pp.rr_item,
    po.rec_qty,
    po.rec_value
   FROM ( SELECT pol.product_id,
            po_1.company_id,
            sum(pol.quantity_done) AS rec_qty,
            sum(pol.quantity_done * pol.discount_price::numeric) AS rec_value
           FROM stock_picking po_1
             JOIN stock_move pol ON po_1.id = pol.picking_id
          WHERE po_1.scheduled_date > '2024-04-01 00:00:00'::timestamp without time zone AND po_1.state::text = 'done'::text AND po_1.origin::text ~~* 'PO/%'::text
          GROUP BY po_1.company_id, pol.product_id) po
     LEFT JOIN product_product pp ON po.product_id = pp.id
     LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
     LEFT JOIN product_category pc ON pt.categ_id = pc.id
     LEFT JOIN res_company rc ON po.company_id = rc.id
     LEFT JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND pt.division_id = cd.company_id
     LEFT JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND pt.brand_id = bd.brand_id
     LEFT JOIN brand br ON bd.brand_id = br.id
  WHERE rc.active = true AND rc.name::text <> 'Ramraj'::text  """)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT rc.state_code,
    rc.distributor_code AS dbrcode,
    rc.name AS distributor_name,
    cd.company_id AS division,
    br.name AS brand,
    pc.name AS category,
    pp.id AS product_id,
    pp.product_variant_name,
    pp.rr_item,
    po.rec_qty,
    po.rec_value
   FROM ( SELECT pol.product_id,
            po_1.company_id,
            sum(pol.quantity_done) AS rec_qty,
            sum(pol.quantity_done * pol.discount_price::numeric) AS rec_value
           FROM stock_picking po_1
             JOIN stock_move pol ON po_1.id = pol.picking_id
          WHERE po_1.scheduled_date > '2024-04-01 00:00:00'::timestamp without time zone AND po_1.state::text = 'done'::text AND po_1.origin::text ~~* 'PO/%'::text
          GROUP BY po_1.company_id, pol.product_id) po
     LEFT JOIN product_product pp ON po.product_id = pp.id
     LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
     LEFT JOIN product_category pc ON pt.categ_id = pc.id
     LEFT JOIN res_company rc ON po.company_id = rc.id
     LEFT JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND pt.division_id = cd.company_id
     LEFT JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND pt.brand_id = bd.brand_id
     LEFT JOIN brand br ON bd.brand_id = br.id
  WHERE rc.active = true AND rc.name::text <> 'Ramraj'::text and rc.distributor_code = %s """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
