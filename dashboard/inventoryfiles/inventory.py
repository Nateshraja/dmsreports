from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from datetime import date, datetime
from dashboard import views
from dashboard.masterfiles import filterfields
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

def get_current_state(request):
    cardcode = request.session.get('param1')
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
    code = request.session.get('param1')
    type_param = request.session.get('param2')

    # Fetch the default state while loading the stock report
    state_param = views.get_current_state_dropdown_options(code)
    #print(state_param)

    # Extract filters from request
    filters = {
        'state': request.GET.get('state', state_param),
        'distributor': request.GET.get('distributor'),
        'division': request.GET.get('division'),
        'category': request.GET.get('category'),
        'brand': request.GET.get('brand'),
        'product': request.GET.get('product'),
    }

    # Base query setup
    base_query = """
        SELECT y.size_name, 
                y.state, 
                y.distributor, 
                y.division, 
                y.brand, 
                y.category, 
                y.product,
                y.product_variant_name,
               y.style_name, 
               y.color_name, 
               y.dist_code,
ROUND(SUM(y.pcs_qty)::NUMERIC, 2) AS total_pcs_qty,
ROUND(SUM(y.box_qty)::NUMERIC, 2) AS total_box_qty,
ROUND(SUM(y.stkvalue)::NUMERIC, 2) AS stkvalue
        FROM (
            SELECT rc.id, rc.state_code AS state, rc.name AS distributor, rc.distributor_code AS dist_code,
                   cd.division_code AS division, pc.name AS category, pc.id AS categ_id,
                   br.name AS brand, br.id AS brnd_id, pt2.name->>'en_US' AS product,
                   pt2.id AS prod_tmp_id, pp.product_variant_name, pp.rr_item, pp.id AS prod_id,uu.ratio, COALESCE(pp.standard_cost, 0) AS standard_cost, cdt.discount,
                   CAST(d.style_name AS TEXT), CAST(d.color_name AS TEXT), CAST(d.size_name AS TEXT),
                   SUM(COALESCE(svl.quantity, 0) * uu.ratio) AS pcs_qty,
                   SUM(COALESCE(svl.quantity, 0)) AS box_qty, 
                    CASE
                        WHEN cd.division_code = 'RR' THEN 
                            SUM(coalesce(svl.quantity,0)) * 
                            (coalesce(pp.standard_cost,0) - coalesce(pp.standard_cost,0) * (coalesce(cdt.discount,0) / 100))
                        ELSE SUM(coalesce(svl.value,0))
                    END AS stkvalue
            FROM res_company rc
            INNER JOIN company_discount cdt ON rc.id = cdt.company_id
            INNER JOIN product_template_res_company_rel pt ON pt.res_company_id = rc.id
            INNER JOIN product_template pt2 ON pt.product_template_id = pt2.id
            INNER JOIN product_product pp ON pt2.id = pp.product_tmpl_id
            INNER JOIN product_category pc ON pt2.categ_id = pc.id
            INNER JOIN res_partner cd ON pt2.division_id = cd.id
            INNER JOIN brand br ON pt2.brand_id = br.id
            INNER JOIN ( 
                SELECT 
                    x.id, 
                    x.ratio::numeric AS ratio
                FROM ( 
                    SELECT 
                        uom_uom.id,
                        CASE
                            WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Dozens' THEN '12'
                            WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Units' THEN '1'
                            ELSE split_part(uom_uom.name ->> 'en_US', '-', 2)
                        END AS ratio
                    FROM uom_uom
                ) x
                WHERE x.ratio <> ''
            ) uu ON pt2.uom_id = uu.id 
            INNER JOIN product_combined_info d ON pp.id = d.vart_id AND pt2.id = d.prod_id  
            LEFT JOIN stock_valuation_layer svl ON svl.company_id = rc.id AND svl.product_id = pp.id
            WHERE rc.active = TRUE
            GROUP BY rc.id, rc.state_code, rc.name, rc.distributor_code, cd.division_code, 
                     pc.name, pc.id, br.name, br.id, pt2.name, pt2.id, pp.product_variant_name, 
                     pp.rr_item, pp.id, uu.ratio, pp.standard_cost, cdt.discount, d.style_name, 
                     d.color_name, d.size_name
    ) y
    WHERE 1=1
    """

    query_params = []

    # Apply different conditions based on `type_param`
    if type_param == 'Ramraj':
        base_query += " AND y.distributor <> 'Ramraj' "
    elif type_param == 'Distributor':
        base_query += " AND y.dist_code = %s "
        query_params.append(code)
    
    # Mandatory condition for state
    base_query += " AND y.state = %s "
    query_params.append(filters['state'])

    # Apply additional filters dynamically
    for key, value in filters.items():
        if value and key != 'state':  # 'state' is already included
            base_query += f" AND y.{key} = %s "
            query_params.append(value)

    # Closing SQL query
    base_query += " GROUP BY y.size_name, y.state,y.product_variant_name, y.distributor, y.division, y.brand, y.category, "
    base_query += " y.product, y.style_name, y.color_name, y.dist_code "
    base_query += " HAVING SUM(y.pcs_qty) > 0 "
    
    #print("Final Query:", base_query)
    #print("Query Params:", query_params)

    with connection.cursor() as cursor:
        cursor.execute(base_query, query_params)
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return JsonResponse(data, safe=False)




def stock_data_old(request):
    # Get session variables
    code = request.session.get('param1')
    type_param = request.session.get('param2')
    filters = {
        'state': request.GET.get('state'),
        'distributor': request.GET.get('distributor'),
        'division': request.GET.get('division'),
        'category': request.GET.get('category'),
        'brand': request.GET.get('brand'),
        'product': request.GET.get('product'),
    }

    filter_conditions = []
    filter_values = []

    for key, value in filters.items():
        if value:  # Add condition only if a filter value is provided
            filter_conditions.append(f"y.{key} = %s")
            filter_values.append(value)
            print(filter_values)
    # Combine the conditions into a single string
    filter_query = " AND ".join(filter_conditions)

    # Append the filters to the query dynamically
    if filter_query:
        filter_query = f" AND {filter_query}"
        
    if code is None:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                # Query to get distinct sizes
                cursor.execute("""
                    SELECT distinct d.sequence,d.size_name
                FROM res_company rc
                INNER JOIN product_template_res_company_rel ptrc ON ptrc.res_company_id = rc.id
                INNER JOIN product_template pt2 ON ptrc.product_template_id = pt2.id
                INNER JOIN product_product pp ON pt2.id = pp.product_tmpl_id
                INNER JOIN product_size_name d ON d.prod_id = pt2.id AND d.vart_id = pp.id
                WHERE 1=1
                order by d.sequence,d.size_name 
                """, [code])
                distinct_sizes = [row[1] for row in cursor.fetchall()]
                #print(distinct_sizes)
                # Query to get stock data
                cursor.execute(f""" select y.sequence,y.size_name,y.state,y.distributor,
                            y.division, y.brand,y.category,y.product,y.product_variant_name, ,y.style_name,y.color_name ,y.pcs_qty ,
                              y.dist_code,y.line_total from (SELECT 
        x.sequence,
        CAST(x.size_name AS TEXT),
        CAST(x.state AS TEXT),
        CAST(x.distributor AS TEXT) ,                               
        CAST(x.division AS TEXT),
        CAST(x.brand AS TEXT),
        CAST(x.category AS TEXT),
        CAST(x.product AS TEXT),
        CAST(x.style_name AS TEXT),
        CAST(x.color_name AS TEXT),
        SUM(COALESCE(a.pcs_qty, 0)) AS pcs_qty, 
        CAST(x.distributor_code AS TEXT) AS dist_code,
        SUM(SUM(COALESCE(a.pcs_qty, 0))) OVER (
            PARTITION BY 
                x.state,
                x.division, 
                x.brand, 
                x.category, 
                x.product, 
                x.style_name, 
                x.color_name, 
                x.distributor_code,
                x.size_name,
                x.sequence
        ) AS line_total -- Line-wise total
    FROM 
    (SELECT 
        rc.id,
        rc.state_code state,
        rc."name" distributor, 
        rc.distributor_code,
        cd.division_code division,
        pt2.division_id AS divi_id,
        pc."name" AS category,
        pc.id AS categ_id,
        br."name" AS brand,
        br.id AS brnd_id,
        pt2."name"->>'en_US' AS product,
        pt2.id AS prod_tmp_id,
        pp.product_variant_name,
        pp.rr_item,
        pp.id AS prod_id,
        uu.ratio,
        COALESCE(pp.standard_cost, 0) AS standard_cost,
        cdt.discount,
        CAST(b.style_name AS TEXT),
        CAST(c.color_name AS TEXT),
        CAST(d.size_name AS TEXT),
        d.sequence
    FROM res_company rc
    INNER JOIN company_discount cdt ON rc.id = cdt.company_id
    INNER JOIN product_template_res_company_rel pt ON pt.res_company_id = rc.id
    INNER JOIN product_template pt2 ON pt.product_template_id = pt2.id
    INNER JOIN product_product pp ON pt2.id = pp.product_tmpl_id
    INNER JOIN product_category pc ON pt2.categ_id = pc.id
    INNER JOIN res_partner cd ON pt2.division_id = cd.id
    INNER JOIN brand br ON pt2.brand_id = br.id
    INNER JOIN ( 
        SELECT 
            x.id, 
            x.ratio::numeric AS ratio
        FROM ( 
            SELECT 
                uom_uom.id,
                CASE
                    WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Dozens' THEN '12'
                    WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Units' THEN '1'
                    ELSE split_part(uom_uom.name ->> 'en_US', '-', 2)
                END AS ratio
            FROM uom_uom
        ) x
        WHERE x.ratio <> ''
    ) uu ON pt2.uom_id = uu.id 
    INNER JOIN dist_divisional_code dd ON dd.id = rc.id
    LEFT JOIN product_size_name d ON pp.product_variant_name = d.product_variant_name and pt2.id = d.prod_id 
    LEFT JOIN product_style_name1 b ON pp.product_variant_name = b.product_variant_name and pt2.id = b.prod_id 
    LEFT JOIN product_color_name c ON pp.product_variant_name = c.product_variant_name and pt2.id = c.prod_id 
    ) x
    LEFT JOIN "Stock_Report_BI" a ON x.product_variant_name = a.product_variant_name AND x.distributor_code = a.dbrcode
    GROUP BY 
        x.size_name,
        x.sequence,
        x.state,
        x.distributor,                               
        x.division, 
        x.brand, 
        x.category, 
        x.product, 
        x.style_name, 
        x.color_name, 
        x.distributor_code
    ORDER BY x.sequence, x.size_name) y where y.distributor<>'Ramraj' {filter_query}
""", [*filter_values])
                stock_rows = cursor.fetchall()

            # Prepare data
            data = []

            # Iterate through stock data
            for row in stock_rows:
                record = {
                    'state': row[2],
                    'distributor': row[3],
                    'division': row[4],
                    'brand': row[5],
                    'category': row[6],
                    'product': row[7],
                    'style_name': row[8],
                    'color_name': row[9],
                    'line_total': row[12],  # Adding the line_total from query
                }
                # Initialize size columns with 0
                for size in distinct_sizes:
                    record[size] = 0

                # Match the size and append the quantity
                matched_size = row[1]  # Assuming the size column is at index 6
                if matched_size in distinct_sizes:
                    record[matched_size] = row[10]  # Quantity at index 7
                #print(data)
                data.append(record)
                #print(record)
            return JsonResponse(data, safe=False)

        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)



    if type_param=='Distributor':
        try:
            with connection.cursor() as cursor:
                # Query to get distinct sizes
                cursor.execute("""
                    SELECT distinct d.sequence,d.size_name
                 FROM res_company rc
                 INNER JOIN product_template_res_company_rel ptrc ON ptrc.res_company_id = rc.id
                 INNER JOIN product_template pt2 ON ptrc.product_template_id = pt2.id
                 INNER JOIN product_product pp ON pt2.id = pp.product_tmpl_id
                 INNER JOIN product_size_name d ON d.prod_id = pt2.id AND d.vart_id = pp.id
                 WHERE rc.distributor_code = %s
                 order by d.sequence,d.size_name 
                """, [code])
                distinct_sizes = [row[1] for row in cursor.fetchall()]
                #print(distinct_sizes)
                # Query to get stock data
                cursor.execute(f""" select y.sequence,y.size_name,y.state,y.distributor,
                            y.division, y.brand,y.category,y.product ,y.style_name,y.color_name ,y.pcs_qty ,
                              y.dist_code,y.line_total  from (SELECT 
        x.sequence,
        CAST(x.size_name AS TEXT),
        CAST(x.state AS TEXT),
        CAST(x.distributor AS TEXT) ,                               
        CAST(x.division AS TEXT),
        CAST(x.brand AS TEXT),
        CAST(x.category AS TEXT),
        CAST(x.product AS TEXT),
        CAST(x.style_name AS TEXT),
        CAST(x.color_name AS TEXT),
        SUM(COALESCE(a.pcs_qty, 0)) AS pcs_qty, 
        CAST(x.distributor_code AS TEXT) AS dist_code,
        SUM(SUM(COALESCE(a.pcs_qty, 0))) OVER (
            PARTITION BY 
                x.state,
                x.division, 
                x.brand, 
                x.category, 
                x.product, 
                x.style_name, 
                x.color_name, 
                x.distributor_code,
                x.size_name,
                x.sequence
        ) AS line_total -- Line-wise total
    FROM 
    (SELECT 
        rc.id,
        rc.state_code state,
        rc."name" distributor, 
        rc.distributor_code,
        cd.division_code division,
        pt2.division_id AS divi_id,
        pc."name" AS category,
        pc.id AS categ_id,
        br."name" AS brand,
        br.id AS brnd_id,
        pt2."name"->>'en_US' AS product,
        pt2.id AS prod_tmp_id,
        pp.product_variant_name,
        pp.rr_item,
        pp.id AS prod_id,
        uu.ratio,
        COALESCE(pp.standard_cost, 0) AS standard_cost,
        cdt.discount,
        CAST(b.style_name AS TEXT),
        CAST(c.color_name AS TEXT),
        CAST(d.size_name AS TEXT),
        d.sequence
     FROM res_company rc
     INNER JOIN company_discount cdt ON rc.id = cdt.company_id
     INNER JOIN product_template_res_company_rel pt ON pt.res_company_id = rc.id
     INNER JOIN product_template pt2 ON pt.product_template_id = pt2.id
     INNER JOIN product_product pp ON pt2.id = pp.product_tmpl_id
     INNER JOIN product_category pc ON pt2.categ_id = pc.id
     INNER JOIN res_partner cd ON pt2.division_id = cd.id
     INNER JOIN brand br ON pt2.brand_id = br.id
     INNER JOIN ( 
         SELECT 
             x.id, 
             x.ratio::numeric AS ratio
         FROM ( 
             SELECT 
                 uom_uom.id,
                 CASE
                     WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Dozens' THEN '12'
                     WHEN split_part(uom_uom.name ->> 'en_US', '-', 1) = 'Units' THEN '1'
                     ELSE split_part(uom_uom.name ->> 'en_US', '-', 2)
                 END AS ratio
             FROM uom_uom
         ) x
         WHERE x.ratio <> ''
     ) uu ON pt2.uom_id = uu.id 
     INNER JOIN dist_divisional_code dd ON dd.id = rc.id
     LEFT JOIN product_size_name d ON pp.product_variant_name = d.product_variant_name and pt2.id = d.prod_id 
     LEFT JOIN product_style_name1 b ON pp.product_variant_name = b.product_variant_name and pt2.id = b.prod_id 
     LEFT JOIN product_color_name c ON pp.product_variant_name = c.product_variant_name and pt2.id = c.prod_id 
    ) x
    LEFT JOIN "Stock_Report_BI" a ON x.product_variant_name = a.product_variant_name AND x.distributor_code = a.dbrcode
    WHERE x.distributor_code = %s
    GROUP BY 
        x.size_name,
        x.sequence,
        x.state,
        x.distributor,                               
        x.division, 
        x.brand, 
        x.category, 
        x.product, 
        x.style_name, 
        x.color_name, 
        x.distributor_code
    ORDER BY x.sequence, x.size_name) y where 1=1 {filter_query}
""", [code, *filter_values])
                stock_rows = cursor.fetchall()

            # Prepare data
            data = []

            # Iterate through stock data
            for row in stock_rows:
                record = {
                    'state': row[2],
                    'distributor': row[3],
                    'division': row[4],
                    'brand': row[5],
                    'category': row[6],
                    'product': row[7],
                    'style_name': row[8],
                    'color_name': row[9],
                    'line_total': row[12],  # Adding the line_total from query
                }
                # Initialize size columns with 0
                for size in distinct_sizes:
                    record[size] = 0

                # Match the size and append the quantity
                matched_size = row[1]  # Assuming the size column is at index 6
                if matched_size in distinct_sizes:
                    record[matched_size] = row[10]  # Quantity at index 7
                #print(data)
                data.append(record)
                #print(record)
            return JsonResponse(data, safe=False)

        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging line
            return JsonResponse({'error': str(e)}, status=500)



def product_report(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    select rc.state_code ,rc."name" ,rc.distributor_code,cd.division_code,pc."name" category,br."name" brnd_name,pt2."name"->>'en_US' prod_name,
pp.product_variant_name,pp.rr_item ,uu.ratio
from res_company rc 
inner join company_discount cdt ON rc.id = cdt.company_id 
inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
inner join product_template pt2 on pt.product_template_id = pt2.id
inner join product_product pp on pt2.id = pp.product_tmpl_id 
inner JOIN product_category pc ON pt2.categ_id = pc.id
inner join res_partner cd ON  pt2.division_id = cd.id
inner JOIN brand br ON pt2.brand_id = br.id
inner JOIN ( SELECT x.id,
            x.ratio::numeric AS ratio
           FROM ( SELECT uom_uom.id,
                        CASE
                            WHEN split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 1) = 'Dozens'::text THEN '12'::text
                            WHEN split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 1) = 'Units'::text THEN '1'::text
                            ELSE split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 2)
                        END AS ratio
                   FROM uom_uom) x
          WHERE x.ratio <> ''::text) uu ON pt2.uom_id = uu.id
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
                    select rc.state_code ,rc."name" ,rc.distributor_code,cd.division_code,pc."name" category,br."name" brnd_name,pt2."name"->>'en_US' prod_name,
pp.product_variant_name,pp.rr_item ,uu.ratio
from res_company rc 
inner join company_discount cdt ON rc.id = cdt.company_id 
inner join product_template_res_company_rel pt on pt.res_company_id  = rc.id 
inner join product_template pt2 on pt.product_template_id = pt2.id
inner join product_product pp on pt2.id = pp.product_tmpl_id 
inner JOIN product_category pc ON pt2.categ_id = pc.id
inner join res_partner cd ON  pt2.division_id = cd.id
inner JOIN brand br ON pt2.brand_id = br.id
inner JOIN ( SELECT x.id,
            x.ratio::numeric AS ratio
           FROM ( SELECT uom_uom.id,
                        CASE
                            WHEN split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 1) = 'Dozens'::text THEN '12'::text
                            WHEN split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 1) = 'Units'::text THEN '1'::text
                            ELSE split_part(uom_uom.name ->> 'en_US'::text, '-'::text, 2)
                        END AS ratio
                   FROM uom_uom) x
          WHERE x.ratio <> ''::text) uu ON pt2.uom_id = uu.id
          where  rc.distributor_code = %s
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def vendor_report(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed

    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 1 as id_count, rc.state_code, rc.name AS dist_name, rc.distributor_code,
                           rp.ref AS cardcode, rp.name, rp.display_name, rp.street, rp.street2, rp.city,
                           rp.state_id, rp.vat, rp.phone, rp.mobile
                    FROM res_partner rp
                    INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id
                    WHERE type = 'contact' """)
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
                    SELECT 1 as id_count, rc.state_code, rc.name AS dist_name, rc.distributor_code,
                           rp.ref AS cardcode, rp.name, rp.display_name, rp.street, rp.street2, rp.city,
                           rp.state_id, rp.vat, rp.phone, rp.mobile
                    FROM res_partner rp
                    INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id
                    WHERE type = 'contact' AND rc.distributor_code = %s
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
