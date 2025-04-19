from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from datetime import date, datetime
from dashboard import views
import json


def stock_report(request):
    context = views.get_session_parameters(request)
    return render(request, 'dashboard/stock/stock.html', context)

def products(request):
    context = {
        'param1': request.session.get('param1', ''),
        'param2': request.session.get('param2', ''),
    }
    # Render the customers.html template with user information
    return render(request, 'dashboard/masters/products.html', context)


def sale_summary_card(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT sum(yearsales) sale_value,sum(yearqty) sale_qty
FROM public."sales_invoice_BI" where 1=1
           """)
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
                    SELECT sum(yearsales) sale_value,sum(yearqty) sale_qty
FROM public."sales_invoice_BI" where distributor_code = %s
group by distributor_code, distributor_name 
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def purchase_summary_card(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select sum(amount) sale_value,sum(qty) sale_qty from (
SELECT rc.id,rc.distributor_code,ya.id,
    ya.company_id,
    d.division_id,
    ya.partner_id,
    ya.state AS order_state,
    yb.state AS line_state,
    ya.date_order,
    count(DISTINCT ya.id) AS year_order_count,
    sum(yb.product_uom_qty) AS qty,
    sum(yb.price_total) AS amount
   FROM res_company rc inner join purchase_order ya on rc.id = ya.company_id 
     JOIN purchase_order_line yb ON ya.id = yb.order_id
     JOIN product_product c ON c.id = yb.product_id
     JOIN product_template d ON c.product_tmpl_id = d.id
  WHERE ya.date_order >= '2024-04-01 00:00:00'::timestamp without time zone
  GROUP BY rc.id,rc.distributor_code,ya.company_id, ya.partner_id, d.division_id, ya.state, yb.state, ya.id) x where 1=1
           """)
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
                    select sum(amount) sale_value,sum(qty) sale_qty from (
SELECT rc.id,rc.distributor_code,ya.id,
    ya.company_id,
    d.division_id,
    ya.partner_id,
    ya.state AS order_state,
    yb.state AS line_state,
    ya.date_order,
    count(DISTINCT ya.id) AS year_order_count,
    sum(yb.product_uom_qty) AS qty,
    sum(yb.price_total) AS amount
   FROM res_company rc inner join purchase_order ya on rc.id = ya.company_id 
     JOIN purchase_order_line yb ON ya.id = yb.order_id
     JOIN product_product c ON c.id = yb.product_id
     JOIN product_template d ON c.product_tmpl_id = d.id
  WHERE ya.date_order >= '2024-04-01 00:00:00'::timestamp without time zone
  GROUP BY rc.id,rc.distributor_code,ya.company_id, ya.partner_id, d.division_id, ya.state, yb.state, ya.id) x where x.distributor_code=%s 
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def stock_summary_card(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                     SELECT 
    SUM(pcs_qty) AS pcs_qty,
    SUM(box_qty) AS box_qty,
    SUM(stkvalue) AS stkvalue
FROM "Stock_Report_BI" srb
WHERE 1=1""")
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
                    SELECT 
    distributor_name,
    SUM(pcs_qty) AS pcs_qty,
    SUM(box_qty) AS box_qty,
    SUM(stkvalue) AS stkvalue
FROM "Stock_Report_BI" srb
WHERE dbrcode = %s
GROUP BY distributor_name 
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def saleordercount(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select today_order_count sale_value from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id
  group by dd.name,dd.distributor_code) x""")
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
                cursor.execute("""select today_order_count sale_value from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id where dd.distributor_code = %s
  group by dd.name,dd.distributor_code) x """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)        


def saleorderQty(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select Todayqty sale_value from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id
  group by dd.name,dd.distributor_code) x""")
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
                cursor.execute("""select Todayqty sale_value from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id where dd.distributor_code = %s
  group by dd.name,dd.distributor_code) x """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)  

def successorder(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select today_order_count sale_value from (   select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id 
    group by dd.name,dd.distributor_code) x""")
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
                cursor.execute("""select today_order_count sale_value from (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id where dd.distributor_code = %s
    group by dd.name,dd.distributor_code) x """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)          

def pendingorder(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select * from (   select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id 
    group by dd.name,dd.distributor_code) x""")
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
                cursor.execute("""select today_order_count sale_value from (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id where dd.distributor_code = %s
    group by dd.name,dd.distributor_code) x """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)         
        
def saleorder_summary(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select sum(today_order_count) today_order_count,sum(Todayqty) Todayqty,sum(Todaysales) Todaysales from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id
  group by dd.name,dd.distributor_code) x""")
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"saleorder_summary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""  select * from ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where 
 t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id  where dd.distributor_code = %s
  group by dd.name,dd.distributor_code) x""", [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"saleorder_summary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)         

def invoice_summary(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""select sum(today_order_count) today_order_count,sum(Todayqty) Todayqty,sum(Todaysales) Todaysales from (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id
    group by dd.name,dd.distributor_code) x """)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"invoice_summary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""select * from (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id where dd.distributor_code = %s
    group by dd.name,dd.distributor_code) x  """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"invoice_summary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)         

def saleorderpending_summary(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute(""" select x.today_order_count-y.today_order_count pending from 
 (select Distributor_Name,distributor_code,today_order_count,Todayqty, Todaysales from 
 ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where  t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id  
  group by dd.name,dd.distributor_code) tx) x
  inner join 
  (select Distributor_Name,distributor_code,today_order_count,Todayqty, Todaysales from 
  (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' 
  group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id  
    group by dd.name,dd.distributor_code) tm) y on x.Distributor_Name=y.Distributor_Name and x.distributor_code=y.distributor_code""")
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"pendingsummary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                cursor.execute(""" select x.today_order_count-y.today_order_count pending from 
 (select Distributor_Name,distributor_code,today_order_count,Todayqty, Todaysales from 
 ( select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount 
  from todayso t where  t.linestate in ('sale','draft')  group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id  where dd.distributor_code = %s
  group by dd.name,dd.distributor_code) tx) x
  inner join 
  (select Distributor_Name,distributor_code,today_order_count,Todayqty, Todaysales from 
  (  select dd.name Distributor_Name,dd.distributor_code,
  sum(coalesce(ti.today_order_count,0)) today_order_count,sum(coalesce(ti.qty,0)) Todayqty,sum(coalesce(ti.amount,0)) Todaysales
  FROM dist_divisional_code dd 
  left join 
  (select company_id,division_id ,min(invoice_date::date) Start_date from invoicedetails where move_type = 'out_invoice' and state = 'posted' 
  group by company_id,division_id) i on dd.id = i.company_id AND dd.company_id = i.division_id
  left join 
  (select t.company_id,t.division_id,sum(t.today_order_count) today_order_count,sum(t.qty) qty, sum(t.amount) amount from todayinvoice t where 
 t.invoice_date :: date = current_date:: date and t.move_type = 'out_invoice' and t.state = 'posted' group by t.company_id,t.division_id)
  ti on dd.id = ti.company_id AND dd.company_id = ti.division_id  where dd.distributor_code = %s
    group by dd.name,dd.distributor_code) tm) y on x.Distributor_Name=y.Distributor_Name and x.distributor_code=y.distributor_code""", [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse({"saleorder_summary": data}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)                 