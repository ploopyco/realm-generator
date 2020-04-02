import flask_wtf
import wtforms
import wtforms.validators
import requests
import uuid
import json


class DonateForm(flask_wtf.FlaskForm):
    amounts = wtforms.RadioField(
        'Amount (everything is in CAD)',
        choices=[
            ('500', '$5'),
            ('1000', '$10'),
            ('1500', '$15'),
            ('2000', '$20'),
            ('5000', '$50'),
            ('10000', '$100')
        ],
        default='500',
        validators=[wtforms.validators.DataRequired()]
    )

    submit = wtforms.SubmitField('Donate')


def process_form(form):
    with open('keys.json', 'r') as json_file:
        keys = json.load(json_file)
        token = keys['token']
        location_id = keys['locationId']

    amount = form.amounts.data

    jdata_ik = str(uuid.uuid4())
    jdata_ord_ik = str(uuid.uuid4())

    jdata = {
        "idempotency_key": jdata_ik,
        "order": {
            "idempotency_key": jdata_ord_ik,
            "order": {
                "location_id": location_id,
                "line_items": [
                    {
                        "name": "Ploopy Donation",
                        "quantity": "1",
                        "base_price_money": {
                            "amount": int(amount),
                            "currency": "CAD"
                        }
                    }
                ]
            }
        },
        "merchant_support_email": "contact@ploopy.co"
    }

    r = requests.post(
        "https://connect.squareup.com/v2/locations/{}/checkouts".format(
            location_id
        ),
        headers={
            "Authorization": "Bearer {}".format(token)
        },
        data=json.dumps(jdata)
    )

    resp = r.json()

    return resp["checkout"]["checkout_page_url"]
