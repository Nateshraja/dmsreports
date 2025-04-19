from django.http import JsonResponse
from django.db import connection
from django.shortcuts import render, redirect
from dashboard import views

def purchase_order(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/purchase/purchase_order.html', context)

def purchase_order_report(request):
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
    po.po_qty,
    po.po_value,
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
          WHERE po_1.date_order >= '2024-04-01 00:00:00'::timestamp without time zone AND po_1.state::text = 'purchase'::text
          GROUP BY po_1.company_id, pol.product_id) po
     JOIN product_product pp ON po.product_id = pp.id
     JOIN product_template pt ON pp.product_tmpl_id = pt.id
     JOIN product_category pc ON pt.categ_id = pc.id
     LEFT JOIN res_company rc ON po.company_id = rc.id
     LEFT JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND pt.division_id = cd.company_id
     LEFT JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND pt.brand_id = bd.brand_id
     LEFT JOIN brand br ON bd.brand_id = br.id
  WHERE rc.active = true AND rc.name::text <> 'Ramraj'::text """)
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
    po.po_qty,
    po.po_value,
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
          WHERE po_1.date_order >= '2024-04-01 00:00:00'::timestamp without time zone AND po_1.state::text = 'purchase'::text
          GROUP BY po_1.company_id, pol.product_id) po
     JOIN product_product pp ON po.product_id = pp.id
     JOIN product_template pt ON pp.product_tmpl_id = pt.id
     JOIN product_category pc ON pt.categ_id = pc.id
     LEFT JOIN res_company rc ON po.company_id = rc.id
     LEFT JOIN company_disibuor_rel cd ON rc.id = cd.disibutor_id AND pt.division_id = cd.company_id
     LEFT JOIN brand_res_company_rel bd ON rc.id = bd.res_company_id AND pt.brand_id = bd.brand_id
     LEFT JOIN brand br ON bd.brand_id = br.id
  WHERE rc.active = true AND rc.name::text <> 'Ramraj'::text AND rc.distributor_code = %s
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



def purchase_return(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/purchase/purchase_return.html', context)

def purchase_return_report(request):
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
                    SELECT 1 as id_count, rc.state_code, rc.name AS dist_name, rc.distributor_code,
                           rp.ref AS cardcode, rp.name, rp.display_name, rp.street, rp.street2, rp.city,
                           rp.state_id, rp.vat, rp.phone, rp.mobile
                    FROM res_partner rp
                    INNER JOIN res_company_res_partner_rel rcr ON rp.id = rcr.res_partner_id
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id  and rc.active = true
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
                    INNER JOIN res_company rc ON rcr.res_company_id = rc.id and rc.active = true
                    WHERE type = 'contact' AND rc.distributor_code = %s
                """, [code])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

            # Convert to JSON
            data = [dict(zip(columns, row)) for row in rows]
            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def purchase_receipt(request):
    context = views.get_session_parameters(request)
    # Render the customers.html template with user information
    return render(request, 'dashboard/purchase/purchase_receipt.html', context)

def purchase_receipt_report(request):
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
