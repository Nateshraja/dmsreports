from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.db import connection
from django.shortcuts import render, redirect
import json
from django.conf import settings

@csrf_exempt
def set_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            param1 = data.get('param1')
            param2 = data.get('param2')
            param3 = get_distributor_name(param1)

            if not param1 or not param2:
                return JsonResponse({"error": "Missing parameters"}, status=400)

            # Store parameters in the session
            request.session['param1'] = param1
            request.session['param2'] = param2
            request.session['param3'] = param3

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def logout_view(request):
    request.session['param1'] = ''
    request.session['param2'] = ''
    request.session['param3'] = ''  # Clears the session
    return JsonResponse({"status": "success"})  # Return JSON response

def get_session_parameters(request):
    return {
        'param1': request.session.get('param1', ''),
        'param2': request.session.get('param2', ''),
        'param3': request.session.get('param3', ''),
        'flex_key': settings.FLEXMONSTER_LICENSE_KEY,
    }

def get_session(request):
    param1 = request.session.get('param1')
    param2 = request.session.get('param2')
    #print(param1)
    if param1 and param2:
        return JsonResponse({'param1': param1, 'param2': param2}, status=200)
    else:
        return JsonResponse({'error': 'Session parameters missing'}, status=404)

def clear_session_parameters(request):
    if request.method == "POST":
        request.session.pop('param1', None)
        request.session.pop('param2', None)
        request.session.pop('param3', None)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def get_distributor_name(parameter1):

    with connection.cursor() as cursor:
        query = """
            SELECT company_display_name
            FROM res_company
            WHERE distributor_code = %s
        """
        cursor.execute(query, [parameter1])
        result = cursor.fetchone()
        #print(result)
        # Return the name if found, or None
        return result[0] if result else None

def get_current_state_dropdown_options(parameter1):

    with connection.cursor() as cursor:
        query = """
            SELECT state_code state
            FROM res_company
            WHERE distributor_code = %s
        """
        cursor.execute(query, [parameter1])
        result = cursor.fetchone()
        #print(result)
        # Return the name if found, or None
        return result[0] if result else None

def get_distributor_display_name(request):
    # Check if the request is a valid Django HttpRequest object
    if not hasattr(request, 'method'):
        return JsonResponse({'error': 'Invalid request object'}, status=400)

    # Handle GET requests only
    if request.method == 'GET':
        param1 = request.GET.get('param1')
        param2 = request.GET.get('param2')

        if not param1 or not param2:
            return JsonResponse({'error': 'Both "param1" and "param2" are required.'}, status=400)

        # If param2 is "Ramraj", return "Ramraj Cotton"
        if param2 == "Ramraj":
            return JsonResponse({'distributor_name': 'Ramraj Cotton'}, status=200)
        if param2 == "Distributor":
        # Query the database to get the distributor display name
            try:
                with connection.cursor() as cursor:
                    query = """
                        SELECT company_display_name
                        FROM res_company
                        WHERE distributor_code = %s
                    """
                    cursor.execute(query, [param1])
                    result = cursor.fetchone()

                    # If no result is found, return an error
                    if not result:
                        return JsonResponse({'error': f'No distributor found for code {param1} and type {param2}'}, status=404)

                    # Return the distributor display name
                    distributor_name = result[0]
                    return JsonResponse({'distributor_name': distributor_name}, status=200)
            except Exception as e:
                # Handle any unexpected errors during query execution
                #print(f"Database error: {e}")
                return JsonResponse({'error': 'An unexpected error occurred while fetching distributor data.'}, status=500)

    # If not a GET request, return a method not allowed response
    return JsonResponse({'error': 'Method not allowed. Only GET requests are supported.'}, status=405)

def testdashboard(request):
    # Pass the parameters to the template context
    context = get_session_parameters(request)
    return render(request, 'dashboard/homepage/testdashboard.html', context)

def reports(request):
    context = get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/homepage/reports.html', context)

def analytics(request):
    context = get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/homepage/analytics.html', context)

def dmsdashboard(request):
    context = get_session_parameters(request)
    return render(request, 'dashboard/homepage/dashboard.html', context)

def login(request):
    return render(request, 'dashboard/homepage/login.html')

'''def dashboard(request):
    cardcode = request.GET.get('param', None)  # Get the parameter from the URL
    print(f"Parameter received: {cardcode}")  # Debugging output

    if cardcode is None:
        return JsonResponse({"error": "Missing parameter: param"}, status=400)

    # Your data fetching logic here...
    # Make sure to use `cardcode` when fetching data

    return render(request, 'dashboard/homepage/dashboard.html', {
        'cardcode': cardcode,  # Pass the parameter to the template
        # Other data you want to send to the template
    })'''





def purchase_return_report(request):
    return render(request, 'dashboard/purchase/purchase_return_report.html')

def receipt_report(request):
    return render(request, 'dashboard/purchase/receipt_report.html')


def daily_stock_report(request):
    return render(request, 'dashboard/stock/daily_stock_report.html')

def sale_order_report(request):
    return render(request, 'dashboard/saleorder/saleorder.html')

def customers_report(request):
    return render(request, 'dashboard/masters/vendors.html')  # Render the stock page

def products_report(request):
    return render(request, 'dashboard/masters/products.html')  # Render the sales page

def vendors_report(request):
    return render(request, 'dashboard/masters/vendors.html')  # Render the sales page

def stock(request):
    return render(request, 'dashboard/stock/stock.html')  # Render the stock page

def customers_report(request):
    cardcode = request.GET.get('param1', None)
    if cardcode is None:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)

    try:
        with connection.cursor() as cursor:
        # Execute the SQL query
            cursor.execute("""
                    SELECT 1 as id_count,rc.state_code, rc.name AS dist_name, rc.distributor_code, rp.ref AS cardcode, 
                   rp.name, rp.display_name, rp.street, rp.street2, rp.city, rp.state_id, 
                   rp.vat, rp.phone, rp.mobile
            FROM res_partner rp
            INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
            INNER JOIN res_company rc ON rcr.res_company_id = rc.id
            WHERE type = 'contact' and rc.distributor_code = %s""", [cardcode])
            # Get the column names from the cursor description
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            data.append(row_dict)
        #print(data)
        # Return the data as JSON response
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def get_current_state(request):
    cardcode = request.session.get('param1')
    #print(cardcode)
    if cardcode is None:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)

    try:
        with connection.cursor() as cursor:
        # Execute the SQL query
            cursor.execute("""
                    SELECT state_code state
            FROM res_company
            WHERE distributor_code = %s""", [cardcode])
            # Get the column names from the cursor description
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            data.append(row_dict)
        #print(data)
        # Return the data as JSON response
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def stock_data(request):
    cardcode = request.GET.get('cardcode', None)

    if cardcode is None:
        return JsonResponse({'error': 'Missing parameter: cardcode'}, status=400)

    try:
        with connection.cursor() as cursor:
            # Execute the query to get stock data including size data as JSON
            cursor.execute("""
                SELECT * FROM dynamic_stock_pivot(%s);
            """, [cardcode])

            rows = cursor.fetchall()

        # Construct the JSON response and dynamically pivot the size_data into columns
        data = []

        for row in rows:
            # Build the base record from the first columns (non-size data)
            record = {
                'divi_id': row[0],
                'brnd_name': row[1],
                'category': row[2],
                'prod_name': row[3],
                'style_name': row[4],
                'color_name': row[5],
                'total_qty': row[6]
            }

            # Get the size_data JSON (7th column in the row)
            size_data = json.loads(row[7])  # Assuming row[7] contains the JSON

            # Dynamically add size columns to the record
            for size, qty in size_data.items():
                record[f'size_{size}'] = qty  # Add a column for each size

            data.append(record)

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


'''def stock_data(request):
    cardcode = request.GET.get('cardcode', None)
    print(f"Parameter received: {cardcode}")
    if cardcode is None:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT  * from public."Stock_Report_BI"  where dbrcode=%s """, [cardcode])  # Replace with your actual table name

            rows = cursor.fetchall()

        # Create a list of dictionaries to return as JSON
        data = [
            {
                'company_id': row[0],
                'state_code': row[1],
                'distributor_code': row[2],
                'distributor_name': row[3],
                'division': row[4],
                'brand': row[5],
                'category': row[6],
                'product_id': row[7],
                'product_variant_name': row[8],
                'rr_item': row[9],
                'box_qty': row[10],
                'pcs_qty': row[11],
                'standard_cost': row[12],
                'stkvalue': row[13],
            }
            for row in rows
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
'''
def sales_data(request):
    cardcode = request.GET.get('cardcode', None)  
    with connection.cursor() as cursor:
        # Execute the SQL query
        cursor.execute("""
                SELECT docentry, discount, walkin_name, walkin_phone, walkin_addr, invno, 
  invoice_user_id, division, brand, state_code, distributor_code, distributor_name, "name",
  rr_item, "ref", cast(yearsales as int) yearsales, yearqty, invoice_date, vp_products, group1, group2, prod_category
FROM public."sales_invoice_BI"  where distributor_code=%s """, [cardcode])
        # Get the column names from the cursor description
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    # Convert rows to list of dictionaries
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        data.append(row_dict)
    #print(data)
    # Return the data as JSON response
    return JsonResponse(data, safe=False)

'''def sales_data(request):
    cardcode = request.GET.get('cardcode', None)  # Get the parameter from the URL
    print(f"Parameter received: {cardcode}")
    with connection.cursor() as cursor:
        # Execute the SQL query
        cursor.execute("""
            SELECT rc.state_code,
                   rc.distributor_code,
                   rc.name AS distributor_name,
                   cd.company_id AS division,
                   br.name AS brand,
                   COALESCE(cdt.discount, 0::double precision) AS disc_per,
                   rp.ref,
                   rp.name,
                   rp.mobile,
                   rp.phone,
                   rp.vat,
                   am.invoice_user_id,
                   am.id AS docentry,
                   am.name AS invno,
                   am.invoice_date,
                   COALESCE(am.walkin_name, ''::character varying) AS walkin_name,
                   COALESCE(am.walkin_phone, ''::character varying) AS walkin_phone,
                   COALESCE(am.walkin_addr, ''::character varying) AS walkin_addr,
                   pc.name AS prod_category,
                   tm.group1,
                   tm.group2,
                   pp.rr_item,
                   pp.product_variant_name AS variantname,
                   --psn.style_name AS style,
                   b.quantity AS yearqty,
                   CASE
                       WHEN tm.vp_products = true THEN b.quantity * tm.vp_products_num::numeric
                       ELSE b.quantity
                   END AS year_sec_qty,
                   b.price_unit,
                   COALESCE(b.price_unit::double precision - b.price_unit::double precision * (cdt.discount / 100::double precision), 0::double precision) AS frate,
                   b.discount,
                   cast(b.price_subtotal AS int) yearsales,
                   b.price_total AS doctotal,
                   CASE
                       WHEN b.discount = 100::numeric THEN
                           CASE
                               WHEN tm.vp_products = true THEN b.quantity * tm.vp_products_num::numeric
                               ELSE b.quantity
                           END
                       ELSE 0::numeric
                   END AS scheme_qty,
                   CASE
                       WHEN b.discount = 100::numeric THEN
                           CASE
                               WHEN tm.vp_products = true THEN b.quantity * tm.vp_products_num::numeric
                               ELSE b.quantity
                           END::double precision * (b.price_unit::double precision - b.price_unit::double precision * (cdt.discount / 100::double precision))
                       ELSE 0::double precision
                   END AS scheme_amt,
                   tm.vp_products
            FROM account_move am
            JOIN account_move_line b ON am.id = b.move_id
            JOIN res_company rc ON am.company_id = rc.id
            JOIN (SELECT a.id,
                         rp_1.id AS partner_id,
                         rp_1.ref,
                         rp_1.name,
                         rp_1.mobile,
                         rp_1.phone,
                         rp_1.vat
                  FROM res_partner a
                  JOIN res_partner rp_1 ON a.commercial_partner_id = rp_1.id) rp ON b.partner_id = rp.id
            JOIN product_product pp ON b.product_id = pp.id
            JOIN product_template tm ON pp.product_tmpl_id = tm.id
            JOIN product_category pc ON tm.categ_id = pc.id
            JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND tm.division_id = cd.company_id
            JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND tm.brand_id = bd.brand_id
            JOIN brand br ON bd.brand_id = br.id
            --JOIN product_style_name psn ON pp.id = psn.product_id AND pp.product_variant_name::text = psn.product_variant_name::text AND tm.id = psn.prd_tmpl_id
            LEFT JOIN company_discount cdt ON rc.id = cdt.company_id
            WHERE  rc.distributor_code = %s and 
            am.state::text = 'posted'::text 
              AND am.move_type::text = 'out_invoice'::text 
              --AND am.invoice_date >= '2024-10-15'::date 
              AND b.name::text <> 'Opening Balance'::text 
              AND NOT (EXISTS (SELECT 1
                               FROM account_move_line aml
                               WHERE aml.name::text = 'Opening Balance'::text 
                                 AND aml.move_id = am.id)) 
              AND rc.active = true 
              AND rc.name::text <> 'Ramraj'::text
        """, [cardcode])

        # Get the column names from the cursor description
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    # Convert rows to list of dictionaries
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        data.append(row_dict)
    #print(data)
    # Return the data as JSON response
    return JsonResponse(data, safe=False)'''


def purchase_data(request):
    cardcode = request.GET.get('cardcode', None)  # Get the parameter from the URL
    with connection.cursor() as cursor:
        # Execute the SQL query
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
    po.po_qty,
    cast(po.po_value as int) po_value,
    po.rec_qty,
    po.rec_value
   FROM ( SELECT pol.product_id,
            po_1.company_id,
            sum(pol.product_qty) AS po_qty,
            sum(pol.product_qty * pol.price_unit - pol.discount_amount::numeric) AS po_value,
            sum(pol.qty_received) AS rec_qty,
            sum(pol.qty_received * pol.price_unit - pol.discount_amount::numeric) AS rec_value
           FROM purchase_order po_1
             JOIN purchase_order_line pol ON po_1.id = pol.order_id
          WHERE --po_1.date_order >= '2024-04-01 00:00:00'::timestamp without time zone AND 
          po_1.state::text = 'purchase'::text
          GROUP BY po_1.company_id, pol.product_id) po
     JOIN product_product pp ON po.product_id = pp.id
     JOIN product_template pt ON pp.product_tmpl_id = pt.id
     JOIN product_category pc ON pt.categ_id = pc.id
     LEFT JOIN res_company rc ON po.company_id = rc.id
     LEFT JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND pt.division_id = cd.company_id
     LEFT JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND pt.brand_id = bd.brand_id
     LEFT JOIN brand br ON bd.brand_id = br.id
  WHERE rc.distributor_code=%s and rc.active = true AND rc.name::text <> 'Ramraj'::text;""", [cardcode])

        # Get the column names from the cursor description
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    # Convert rows to list of dictionaries
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        data.append(row_dict)
    #print(data)
    # Return the data as JSON response
    return JsonResponse(data, safe=False)
