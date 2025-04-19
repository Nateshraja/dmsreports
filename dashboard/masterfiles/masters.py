from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from dashboard import views

def customers(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/masters/customers.html', context)

def products(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/masters/products.html', context)


def vendors(request):
   context = views.get_session_parameters(request)
   return render(request, 'dashboard/masters/vendors.html', context)  # Render the dashboard page


def customers_report(request):
    # Retrieve parameters from GET request
    code = request.session.get('param1')
    type_param = request.session.get('param2')  # Not used in query but available if needed


    if not code:
        return JsonResponse({'error': 'Missing parameter: code'}, status=400)
    if type_param=='Ramraj':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT length(rp.ref) as id_count,ar.name area_code, rc.state_code, rc.name AS dist_name, rc.distributor_code,
                           rp.ref AS cardcode, rp.name customer, rp.display_name, rp.street, rp.street2, rp.city,
                           rp.state_id, rp.vat, rp.phone, rp.mobile 
                    FROM res_partner rp
                    INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id  and rc.active = true
                    inner join area ar on ar.id = rp.area
                    WHERE type = 'contact' and rp.active=true """)
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
                    SELECT length(rp.ref) as id_count,ar.name area_code, rc.state_code, rc.name AS dist_name, rc.distributor_code,
                           rp.ref AS cardcode, rp.name customer, rp.display_name, rp.street, rp.street2, rp.city,
                           rp.state_id, rp.vat, rp.phone, rp.mobile ,*
                    FROM res_partner rp
                    INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id  and rc.active = true
                    inner join area ar on ar.id = rp.area
                    WHERE type = 'contact' and rp.active=true AND rc.distributor_code = %s
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
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
                    SELECT distinct cd.division_code AS division, pc.name AS category, pc.id AS categ_id,
                   br.name AS brand, pt2.group1,pt2.group2,br.id AS brnd_id, pt2.name->>'en_US' AS product,
                   pt2.id AS prod_tmp_id, pp.product_variant_name, pp.rr_item, pp.id AS prod_id,uu.ratio,
                                COALESCE(pp.standard_cost, 0) AS standard_cost,
                   CAST(d.style_name AS TEXT), CAST(d.color_name AS TEXT), CAST(d.size_name AS TEXT) ,
                               concat(pt2.name->>'en_US',' (Size: ',d.size_name,' , Color: ',d.color_name,' , Style: ',d.style_name,' )') dms_name    
			from product_template pt2 
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
                    select rc.state_code ,rc."name" distributor,rc.distributor_code,cd.division_code AS division,
                                pc.name AS category, pc.id AS categ_id,
                   br.name AS brand, pt2.group1,pt2.group2,br.id AS brnd_id, pt2.name->>'en_US' AS product,
                   pt2.id AS prod_tmp_id, pp.product_variant_name, pp.rr_item, pp.id AS prod_id,uu.ratio, 
                               COALESCE(pp.standard_cost, 0) AS standard_cost, cdt.discount,
                   CAST(d.style_name AS TEXT), CAST(d.color_name AS TEXT), CAST(d.size_name AS TEXT)  ,
                               concat(pt2.name->>'en_US',' (Size: ',d.size_name,' , Color: ',d.color_name,' , Style: ',d.style_name,' )') dms_name  
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
            INNER JOIN product_combined_info d ON pp.id = d.vart_id AND pt2.id = d.prod_id
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
