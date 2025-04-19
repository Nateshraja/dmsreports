from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from datetime import date, datetime
from dashboard import views
import json

def sales_qty_pivot(request):
   context = views.get_session_parameters(request)
   return render(request, 'dashboard/analytics/salesqtycomparison.html', context)  # Render the dashboard page

def sales_value_pivot(request):
   context = views.get_session_parameters(request)
   return render(request, 'dashboard/analytics/salesvaluecomparison.html', context)  # Render the dashboard page

def sales_summary_pivot(request):
   context = views.get_session_parameters(request)
   return render(request, 'dashboard/analytics/salessummarypivot.html', context)  # Render the dashboard page


def get_chart_data(request, report_type):
    code = request.session.get('param1', '')
    type_param = request.session.get('param2', '')

    #print(f"📌 Received report_type: {report_type}")
    #print(f"📌 Session param1 (code): {code}")
    #print(f"📌 Session param2 (type_param): {type_param}")

    # Queries for 'Ramraj'
    if type_param == 'Ramraj':
        query_dict = {
            "overall": """SELECT TO_CHAR(invoice_date, 'YYYY-MM') as month, SUM(inv_amt) AS total_sales 
                          FROM "Monthly_Divisionwise_Sales_Report"
                          WHERE concat(date_part('year'::text, CURRENT_DATE)-1, '-03') < TO_CHAR(invoice_date, 'YYYY-MM')
                          GROUP BY month
                          ORDER BY month;""",

            "top-sales": """SELECT product_name, SUM(inv_qty) AS quantity  
                            FROM "Monthly_Divisionwise_Sales_Report"
                            WHERE concat(date_part('year'::text, CURRENT_DATE)-1, '-03') < TO_CHAR(invoice_date, 'YYYY-MM')
                            GROUP BY product_name 
                            ORDER BY quantity DESC LIMIT 10;""",

            "top-customer": """SELECT cus_name, SUM(inv_amt) AS total_spent  
                               FROM "Monthly_Divisionwise_Sales_Report"
                               WHERE concat(date_part('year'::text, CURRENT_DATE)-1, '-03') < TO_CHAR(invoice_date, 'YYYY-MM')
                               GROUP BY cus_name 
                               ORDER BY total_spent DESC LIMIT 10;""",

            "big-deals": """SELECT invno, cus_name, cardcode, SUM(inv_amt) AS inv_amt
                            FROM "Monthly_Divisionwise_Sales_Report"
                            GROUP BY invno, cus_name, cardcode
                            ORDER BY SUM(inv_amt) DESC LIMIT 10;""",

            "brand": """SELECT brand, SUM(stkvalue) AS sales 
                        FROM "Stock_Report_BI"
                        GROUP BY brand 
                        ORDER BY brand;""",

            "category": """SELECT category, SUM(pcs_qty) AS quantity 
                           FROM "Stock_Report_BI"
                           GROUP BY category 
                           ORDER BY category DESC;""",

            "group1": """SELECT division, SUM(stkvalue) AS total_spent 
                         FROM "Stock_Report_BI"
                         GROUP BY division;"""
        }

    # Queries for 'Distributor'
    elif type_param == 'Distributor':
        query_dict = {
            "overall": """SELECT TO_CHAR(invoice_date, 'YYYY-MM') as month, SUM(inv_amt) AS total_sales 
                          FROM "Monthly_Divisionwise_Sales_Report"
                          WHERE distributor_code = %s AND concat(date_part('year'::text, CURRENT_DATE)-1, '-03') < TO_CHAR(invoice_date, 'YYYY-MM')
                          GROUP BY month
                          ORDER BY month;""",

            "top-sales": """SELECT product_name, SUM(inv_qty) AS quantity  
                            FROM "Monthly_Divisionwise_Sales_Report"
                            WHERE distributor_code = %s AND concat(date_part('year'::text, CURRENT_DATE)-1, '-03') < TO_CHAR(invoice_date, 'YYYY-MM')
                            GROUP BY product_name 
                            ORDER BY quantity DESC LIMIT 10;""",

            "top-customer": """SELECT cus_name, SUM(inv_amt) AS total_spent  
                               FROM "Monthly_Divisionwise_Sales_Report"
                               WHERE distributor_code = %s
                               GROUP BY cus_name 
                               ORDER BY total_spent DESC LIMIT 10;""",

            "big-deals": """SELECT invno, cus_name, cardcode, SUM(inv_amt) AS inv_amt
                            FROM "Monthly_Divisionwise_Sales_Report"
                            WHERE distributor_code = %s
                            GROUP BY invno, cus_name, cardcode
                            ORDER BY SUM(inv_amt) DESC LIMIT 10;""",

            "brand": """SELECT brand, SUM(stkvalue) AS sales 
                        FROM "Stock_Report_BI"
                        WHERE dbrcode = %s
                        GROUP BY brand 
                        ORDER BY brand;""",

            "category": """SELECT category, SUM(pcs_qty) AS quantity 
                           FROM "Stock_Report_BI"
                           WHERE dbrcode = %s
                           GROUP BY category 
                           ORDER BY category DESC;""",

            "division": """SELECT division, SUM(stkvalue) AS total_spent 
                         FROM "Stock_Report_BI"
                         WHERE dbrcode = %s
                         GROUP BY division;"""
        }

    else:
        return JsonResponse({"error": "Invalid type_param"}, status=400)

    # Validate report type
    if report_type not in query_dict:
        return JsonResponse({"error": "Invalid report type"}, status=400)

    # Execute query
    query = query_dict[report_type]
    params = [code] if type_param == 'Distributor' else []

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()

        # Convert to JSON format
        result_data = []
        for row in data:
            result_data.append(dict(zip([desc[0] for desc in cursor.description], row)))

        return JsonResponse(result_data, safe=False)

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
        return JsonResponse({'error': str(e)}, status=500)

def get_stock_chart_data(request, report_type):
    code = request.session.get('param1', '')
    type_param = request.session.get('param2', '')

    #print(f"📌 Received report_type: {report_type}")
    #print(f"📌 Session param1 (code): {code}")
    #print(f"📌 Session param2 (type_param): {type_param}")

    # Queries for 'Ramraj'
    if type_param == 'Ramraj':
        query_dict = {
            "brand": """SELECT brand,sum(pcs_qty) qty ,SUM(stkvalue) AS sales 
                        FROM "Stock_Report_BI"
                        GROUP BY brand 
                        ORDER BY brand;""",

            "category": """SELECT category, SUM(pcs_qty) AS qty ,SUM(stkvalue) AS sales
                           FROM "Stock_Report_BI"
                           GROUP BY category 
                           ORDER BY category DESC;""",

            "group1": """SELECT division, SUM(stkvalue) AS total_spent 
                         FROM "Stock_Report_BI"
                         GROUP BY division;"""
        }

    # Queries for 'Distributor'
    elif type_param == 'Distributor':
        query_dict = {
            "brand": """SELECT brand,sum(pcs_qty) qty ,SUM(stkvalue) AS sales 
                        FROM "Stock_Report_BI"
                        WHERE dbrcode = %s
                        GROUP BY brand 
                        ORDER BY brand;""",

            "category": """SELECT category, SUM(pcs_qty) AS qty ,SUM(stkvalue) AS sales
                           FROM "Stock_Report_BI"
                           WHERE dbrcode = %s
                           GROUP BY category 
                           ORDER BY category DESC;""",

            "division": """SELECT division, SUM(stkvalue) AS total_spent 
                         FROM "Stock_Report_BI"
                         WHERE dbrcode = %s
                         GROUP BY division;"""
        }

    else:
        return JsonResponse({"error": "Invalid type_param"}, status=400)

    # Validate report type
    if report_type not in query_dict:
        return JsonResponse({"error": "Invalid report type"}, status=400)

    # Execute query
    query = query_dict[report_type]
    params = [code] if type_param == 'Distributor' else []

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            data = cursor.fetchall()

        # Convert to JSON format
        result_data = []
        for row in data:
            result_data.append(dict(zip([desc[0] for desc in cursor.description], row)))

        return JsonResponse(result_data, safe=False)

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
        return JsonResponse({'error': str(e)}, status=500)




def stock_report(request):
    context = views.get_session_parameters(request)
    return render(request, 'dashboard/stock/stock.html', context)

def products(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/masters/products.html', context)


def sales_chart(request):
    context = views.get_session_parameters(request)
    
    # Render the analytics.html template with the context data
    return render(request, 'dashboard/analytics/salesdata.html', context)

def purchase_chart(request):
    context = views.get_session_parameters(request)
    
    # Render the analytics.html template with the context data
    return render(request, 'dashboard/analytics/purchasedata.html', context)

def stock_chart(request):
    context = views.get_session_parameters(request)
    
    # Render the analytics.html template with the context data
    return render(request, 'dashboard/analytics/stockdata.html', context)

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
        
def analytics_monthly_sales_data(request):
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    from_date = request.GET.get('from_date', '')  # Get 'from_date' from request
    to_date = request.GET.get('to_date', '')  # Get 'to_date' from request

    # Base query
    base_query = """
        SELECT TO_CHAR(invoice_date, 'YYYY-MM') AS month, SUM(yearsales) AS total_sales
        FROM "sales_invoice_BI"
        WHERE 1=1
    """

    query_params = []  # List to hold query parameters

    # Apply from_date filter
    if from_date:
        base_query += " AND invoice_date >= %s"
        query_params.append(from_date)

    # Apply to_date filter
    if to_date:
        base_query += " AND invoice_date <= %s"
        query_params.append(to_date)

    # Additional conditions based on `type_param`
    if type_param == 'Ramraj':
        base_query += " AND 1=1"  # No specific condition, but keeps structure
    elif type_param == 'Distributor':
        base_query += " AND distributor_code = %s"
        query_params.append(code)

    # Group by and order by clause
    base_query += " GROUP BY month ORDER BY month"

    try:
        with connection.cursor() as cursor:
            cursor.execute(base_query, query_params)
            data = cursor.fetchall()

        # Convert data into JSON format
        sales_data = {"months": [], "totals": []}
        for row in data:
            sales_data["months"].append(row[0])  # 'YYYY-MM'
            sales_data["totals"].append(float(row[1]))  # Sales amount
        
        print(sales_data)  # Debugging
        return JsonResponse(sales_data)

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
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
        

def sales_qty_pivot_view(request):
    try:
        code = request.session.get('param1')
        type_param = request.session.get('param2')
        distributor = request.GET.get('distributor')
        state_code = request.GET.get('state_code')
        
        # Fetch unique month-year combinations with correct fiscal order
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT 
                    CONCAT(
                        CHR(64 + 
                            CAST(
                                CASE 
                                    WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3
                                    ELSE EXTRACT(MONTH FROM invoice_date) + 9
                                END 
                            AS INT)
                        ), 
                        '-', TO_CHAR(invoice_date, 'Mon-YYYY')
                    ) AS month
                FROM "DMS_Sales_Invoice_BI"
                ORDER BY month;
            """)
            months = [row[0] for row in cursor.fetchall()]
        
        # Construct pivot query dynamically
        month_columns = ", ".join([
            f"""COALESCE(SUM(CASE 
                WHEN CONCAT(
                    CHR(64 + CAST(
                        CASE 
                            WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3 
                            ELSE EXTRACT(MONTH FROM invoice_date) + 9 
                        END AS INT)
                    ), '-', TO_CHAR(invoice_date, 'Mon-YYYY')) = '{month}' 
                THEN yearqty 
                END), 0) AS "{month}" """
            for month in months
        ])

        # Base Query
        base_query = f"""
            SELECT 
                a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name,
                {month_columns}
            FROM "DMS_Sales_Invoice_BI" a
            INNER JOIN product_combined_info b ON a.product_id = b.vart_id
            WHERE 1=1
        """
        
        # Apply Filters
        conditions = []
        params = []
        
        if type_param == 'Distributor':
            conditions.append(" a.distributor_code = %s ")
            params.append(code)
        if distributor:
            conditions.append(" a.distributor_name = %s ")
            params.append(distributor)
        if state_code:
            conditions.append(" a.state_code = %s ")
            params.append(state_code)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " GROUP BY a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name order by a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name"
        
        # Execute the Query
        with connection.cursor() as cursor:
            cursor.execute(base_query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return JsonResponse(results, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def sales_value_pivot_view(request):
    try:
        code = request.session.get('param1')
        type_param = request.session.get('param2')
        distributor = request.GET.get('distributor')
        state_code = request.GET.get('state_code')
        
        # Fetch unique month-year combinations with correct fiscal order
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT 
                    CONCAT(
                        CHR(64 + 
                            CAST(
                                CASE 
                                    WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3
                                    ELSE EXTRACT(MONTH FROM invoice_date) + 9
                                END 
                            AS INT)
                        ), 
                        '-', TO_CHAR(invoice_date, 'Mon-YYYY')
                    ) AS month
                FROM "DMS_Sales_Invoice_BI"
                ORDER BY month;
            """)
            months = [row[0] for row in cursor.fetchall()]
        
        # Construct pivot query dynamically
        month_columns = ", ".join([
            f"""COALESCE(SUM(CASE 
                WHEN CONCAT(
                    CHR(64 + CAST(
                        CASE 
                            WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3 
                            ELSE EXTRACT(MONTH FROM invoice_date) + 9 
                        END AS INT)
                    ), '-', TO_CHAR(invoice_date, 'Mon-YYYY')) = '{month}' 
                THEN yearsales 
                END), 0) AS "{month}" """
            for month in months
        ])

        # Base Query
        base_query = f"""
            SELECT 
                a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name,
                {month_columns}
            FROM "DMS_Sales_Invoice_BI" a
            INNER JOIN product_combined_info b ON a.product_id = b.vart_id
            WHERE 1=1
        """
        
        # Apply Filters
        conditions = []
        params = []
        
        if type_param == 'Distributor':
            conditions.append(" a.distributor_code = %s ")
            params.append(code)
        if distributor:
            conditions.append(" a.distributor_name = %s ")
            params.append(distributor)
        if state_code:
            conditions.append(" a.state_code = %s ")
            params.append(state_code)
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " GROUP BY a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name order by a.state_code, a.distributor_code, a.distributor_name, a.group1, a.group2, b.style_name"
        
        # Execute the Query
        with connection.cursor() as cursor:
            cursor.execute(base_query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return JsonResponse(results, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def sales_summary_pivot_view(request):
    try:
        code = request.session.get('param1')
        type_param = request.session.get('param2')
        distributor = request.GET.get('distributor')
        state_code = request.GET.get('state_code')

        # Fetch unique month-year combinations
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT 
                    CONCAT(
                        CHR(64 + 
                            CAST(
                                CASE 
                                    WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3
                                    ELSE EXTRACT(MONTH FROM invoice_date) + 9
                                END 
                            AS INT)
                        ), 
                        '-', TO_CHAR(invoice_date, 'Mon-YYYY')
                    ) AS month
                FROM "DMS_Sales_Invoice_BI"
                ORDER BY month;
            """)
            months = [row[0] for row in cursor.fetchall()]

        # Construct pivot query with Quantity and Value for each month
        month_columns = ", ".join([
            f"""COALESCE(SUM(CASE 
                WHEN CONCAT(
                    CHR(64 + CAST(
                        CASE 
                            WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3 
                            ELSE EXTRACT(MONTH FROM invoice_date) + 9 
                        END AS INT)
                    ), '-', TO_CHAR(invoice_date, 'Mon-YYYY')) = '{month}' 
                THEN yearqty 
                END), 0) AS "{month} QTY",

                COALESCE(SUM(CASE 
                WHEN CONCAT(
                    CHR(64 + CAST(
                        CASE 
                            WHEN EXTRACT(MONTH FROM invoice_date) >= 4 THEN EXTRACT(MONTH FROM invoice_date) - 3 
                            ELSE EXTRACT(MONTH FROM invoice_date) + 9 
                        END AS INT)
                    ), '-', TO_CHAR(invoice_date, 'Mon-YYYY')) = '{month}' 
                THEN yearsales 
                END), 0) AS "{month} VALUE" """
            for month in months
        ])

        base_query = f"""
            SELECT 
                state_code, distributor_code, distributor_name, group1, 
                {month_columns}
            FROM "DMS_Sales_Invoice_BI"
            WHERE 1=1
        """

        # Apply Filters
        conditions = []
        params = []

        if type_param == 'Distributor':
            conditions.append(" distributor_code = %s ")
            params.append(code)
        if distributor:
            conditions.append(" distributor_name = %s ")
            params.append(distributor)
        if state_code:
            conditions.append(" state_code = %s ")
            params.append(state_code)

        # Add conditions dynamically
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        base_query += " GROUP BY state_code, distributor_code, distributor_name, group1 ORDER BY state_code, distributor_code, distributor_name, group1"

        # Execute the Query
        with connection.cursor() as cursor:
            cursor.execute(base_query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse(results, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

