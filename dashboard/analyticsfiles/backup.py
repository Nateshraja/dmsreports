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


def sales_chart(request):
    context = {
        'param1': request.session.get('param1', ''),
        'param2': request.session.get('param2', ''),
    }
    # Render the customers.html template with user information
    return render(request, 'dashboard/homepage/analytics.html', context)

def monthly_sales_data(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')
    if type_param=='Ramraj':
        try:                      
            query = """
                SELECT TO_CHAR(invoice_date, 'YYYY-MM') AS month, SUM(yearsales) AS total_sales
                FROM "sales_invoice_BI"  -- Replace with your actual table name
                where 1=1  and concat(date_part('year'::text, CURRENT_DATE)-1,'-03')<TO_CHAR(invoice_date, 'YYYY-MM')
                GROUP BY month
                ORDER BY month;
            """
            
            with connection.cursor() as cursor:
                cursor.execute(query,[code])
                data = cursor.fetchall()

            # Convert data into JSON format
            sales_data = {"months": [], "totals": []}
            for row in data:
                sales_data["months"].append(row[0])  # 'YYYY-MM'
                sales_data["totals"].append(float(row[1]))  # Sales amount

            return JsonResponse(sales_data)
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)
    if type_param=='Distributor':
        try:                      
            query = """
                SELECT TO_CHAR(invoice_date, 'YYYY-MM') AS month, SUM(yearsales) AS total_sales
                FROM "sales_invoice_BI"  -- Replace with your actual table name
                where distributor_code =%s  and concat(date_part('year'::text, CURRENT_DATE)-1,'-03')<TO_CHAR(invoice_date, 'YYYY-MM')
                GROUP BY month
                ORDER BY month;
            """
            
            with connection.cursor() as cursor:
                cursor.execute(query,[code])
                data = cursor.fetchall()

            # Convert data into JSON format
            sales_data = {"months": [], "totals": []}
            for row in data:
                sales_data["months"].append(row[0])  # 'YYYY-MM'
                sales_data["totals"].append(float(row[1]))  # Sales amount

            return JsonResponse(sales_data)
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)       



def monthly_sales_table_chart(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')
    if type_param=='Ramraj':
        try:            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT group1,
                        (SUM(inv_qty) - SUM(ret_qty)) - SUM(schemeqty) AS inv_qty,
                        SUM(schemeqty) AS schemeqty,
                        (SUM(inv_qty) - SUM(ret_qty)) AS final_qty
                    FROM "Monthly_Divisionwise_Sales_Report"
                               where 1=1  and date_part('year'::text, invoice_date::date) = date_part('year'::text, CURRENT_DATE)
                    GROUP BY group1
                """)
                rows = cursor.fetchall()

            # Convert data into JSON format
            data = {
                "group1": [row[0] for row in rows],       # Labels (Groups)
                "inv_qty": [row[1] for row in rows],      # Inventory Quantity
                "schemeqty": [row[2] for row in rows],    # Scheme Quantity
                "final_qty": [row[3] for row in rows]     # Final Quantity
            }

            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)
        
    if type_param=='Distributor':
        try:            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT group1,
                        (SUM(inv_qty) - SUM(ret_qty)) - SUM(schemeqty) AS inv_qty,
                        SUM(schemeqty) AS schemeqty,
                        (SUM(inv_qty) - SUM(ret_qty)) AS final_qty
                    FROM "Monthly_Divisionwise_Sales_Report" where distributor_code = %s
                               and date_part('year'::text, invoice_date::date) = date_part('year'::text, CURRENT_DATE)
                    GROUP BY group1
                """,[code])
                rows = cursor.fetchall()

            # Convert data into JSON format
            data = {
                "group1": [row[0] for row in rows],       # Labels (Groups)
                "inv_qty": [row[1] for row in rows],      # Inventory Quantity
                "schemeqty": [row[2] for row in rows],    # Scheme Quantity
                "final_qty": [row[3] for row in rows]     # Final Quantity
            }

            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)
        



        