from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, List, Annotated
from pydantic import ValidationError

from src.configuration.db_service import default_db
from src.configuration.db_models import (
    SalesReportRequestCreateDto,
    SalesReportRequestUpdateDto,
    RecipientEmail,
    KpiPeriodsEnum,
    SalesGroupingsEnum,
    SalesCurrencyEnum,
)
from src.configuration.crontab import (
    CrontabFrequency,
)
from src.frontend.templates_config import templates

router = APIRouter()


@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    """Show form to create a new sales report request."""
    return templates.TemplateResponse(
        "sales_report_form.html",
        {
            "request": request,
            "mode": "create",
            "periods": list(KpiPeriodsEnum),
            "groupings": list(SalesGroupingsEnum),
            "currencies": list(SalesCurrencyEnum),
            "form_data": {
                "period": KpiPeriodsEnum.MONTHLY.value,
                "grouping": None,
                "grouping_value": "",
                "currency": SalesCurrencyEnum.FUNCTIONAL.value,
                "recipients": [{"email": "", "name": ""}],
            },
        },
    )


@router.get("/edit/{request_id}", response_class=HTMLResponse)
async def edit_form(request: Request, request_id: int):
    """Show form to edit an existing sales report request."""
    try:
        # Find the request by ID
        existing_requests = default_db.get_all_sales_report_requests()
        sales_request = next(
            (req for req in existing_requests if req.id == request_id), None
        )

        if not sales_request:
            raise HTTPException(
                status_code=404, detail="Sales report request not found"
            )

        form_data = {
            "period": sales_request.period.value,
            "grouping": sales_request.grouping.value
            if sales_request.grouping
            else None,
            "grouping_value": sales_request.grouping_value or "",
            "currency": sales_request.currency.value,
            "recipients": [
                {"email": rec.email, "name": rec.name}
                for rec in sales_request.recipients
            ],
        }

        return templates.TemplateResponse(
            "sales_report_form.html",
            {
                "request": request,
                "mode": "edit",
                "request_id": request_id,
                "sales_request": sales_request,
                "periods": list(KpiPeriodsEnum),
                "groupings": list(SalesGroupingsEnum),
                "currencies": list(SalesCurrencyEnum),
                "form_data": form_data,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading request: {str(e)}")


@router.post("/create")
async def create_request(
    request: Request,
    period: Annotated[str, Form()],
    currency: Annotated[str, Form()],
    grouping: Annotated[Optional[str], Form()] = None,
    grouping_value: Annotated[Optional[str], Form()] = None,
    recipient_emails: Annotated[List[str], Form()] = [],
    recipient_names: Annotated[List[str], Form()] = [],
):
    """Create a new sales report request."""
    try:
        # Parse form data
        period_enum = KpiPeriodsEnum(period)
        grouping_enum = (
            SalesGroupingsEnum(grouping) if grouping and grouping != "" else None
        )
        currency_enum = SalesCurrencyEnum(currency)

        # Process recipients
        recipients = []
        for email, name in zip(recipient_emails, recipient_names):
            email = email.strip()
            name = name.strip()
            if email and name:  # Only add if both are provided
                recipients.append(RecipientEmail(email=email, name=name))

        # Validate form data
        errors = validate_form_data(
            period_enum, grouping_enum, grouping_value, currency_enum, recipients
        )

        if errors:
            form_data = {
                "period": period,
                "grouping": grouping,
                "grouping_value": grouping_value or "",
                "currency": currency,
                "recipients": [
                    {"email": email, "name": name}
                    for email, name in zip(recipient_emails, recipient_names)
                ],
            }
            return templates.TemplateResponse(
                "sales_report_form.html",
                {
                    "request": request,
                    "mode": "create",
                    "periods": list(KpiPeriodsEnum),
                    "groupings": list(SalesGroupingsEnum),
                    "currencies": list(SalesCurrencyEnum),
                    "form_data": form_data,
                    "errors": errors,
                },
            )

        # Create request
        request_data = SalesReportRequestCreateDto(
            period=period_enum,
            grouping=grouping_enum,
            grouping_value=grouping_value if grouping_enum else None,
            currency=currency_enum,
            recipients=recipients,
        )

        result = default_db.create_sales_report_request(request_data)

        # Redirect to main page with success message
        return RedirectResponse(
            url=f"/?success=Created sales report request: {result.name}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as e:
        form_data = {
            "period": period,
            "grouping": grouping,
            "grouping_value": grouping_value or "",
            "currency": currency,
            "recipients": [
                {"email": email, "name": name}
                for email, name in zip(recipient_emails, recipient_names)
            ],
        }
        return templates.TemplateResponse(
            "sales_report_form.html",
            {
                "request": request,
                "mode": "create",
                "periods": list(KpiPeriodsEnum),
                "groupings": list(SalesGroupingsEnum),
                "currencies": list(SalesCurrencyEnum),
                "form_data": form_data,
                "errors": [f"Error creating request: {str(e)}"],
            },
        )


@router.post("/edit/{request_id}")
async def update_request(
    request: Request,
    request_id: int,
    period: Annotated[str, Form()],
    currency: Annotated[str, Form()],
    grouping: Annotated[Optional[str], Form()] = None,
    grouping_value: Annotated[Optional[str], Form()] = None,
    recipient_emails: Annotated[List[str], Form()] = [],
    recipient_names: Annotated[List[str], Form()] = [],
):
    """Update an existing sales report request."""
    try:
        # Parse form data
        period_enum = KpiPeriodsEnum(period)
        grouping_enum = (
            SalesGroupingsEnum(grouping) if grouping and grouping != "" else None
        )
        currency_enum = SalesCurrencyEnum(currency)

        # Process recipients
        recipients = []
        for email, name in zip(recipient_emails, recipient_names):
            email = email.strip()
            name = name.strip()
            if email and name:  # Only add if both are provided
                recipients.append(RecipientEmail(email=email, name=name))

        # Validate form data
        errors = validate_form_data(
            period_enum, grouping_enum, grouping_value, currency_enum, recipients
        )

        if errors:
            # Get the original request for display
            existing_requests = default_db.get_all_sales_report_requests()
            sales_request = next(
                (req for req in existing_requests if req.id == request_id), None
            )

            form_data = {
                "period": period,
                "grouping": grouping,
                "grouping_value": grouping_value or "",
                "currency": currency,
                "recipients": [
                    {"email": email, "name": name}
                    for email, name in zip(recipient_emails, recipient_names)
                ],
            }
            return templates.TemplateResponse(
                "sales_report_form.html",
                {
                    "request": request,
                    "mode": "edit",
                    "request_id": request_id,
                    "sales_request": sales_request,
                    "periods": list(KpiPeriodsEnum),
                    "groupings": list(SalesGroupingsEnum),
                    "currencies": list(SalesCurrencyEnum),
                    "form_data": form_data,
                    "errors": errors,
                },
            )

        # Update request
        request_data = SalesReportRequestUpdateDto(
            id=request_id,
            period=period_enum,
            grouping=grouping_enum,
            grouping_value=grouping_value if grouping_enum else None,
            currency=currency_enum,
            recipients=recipients,
        )

        result = default_db.update_sales_report_request(request_data)

        # Redirect to main page with success message
        return RedirectResponse(
            url=f"/?success=Updated sales report request: {result.name}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as e:
        # Get the original request for display
        existing_requests = default_db.get_all_sales_report_requests()
        sales_request = next(
            (req for req in existing_requests if req.id == request_id), None
        )

        form_data = {
            "period": period,
            "grouping": grouping,
            "grouping_value": grouping_value or "",
            "currency": currency,
            "recipients": [
                {"email": email, "name": name}
                for email, name in zip(recipient_emails, recipient_names)
            ],
        }
        return templates.TemplateResponse(
            "sales_report_form.html",
            {
                "request": request,
                "mode": "edit",
                "request_id": request_id,
                "sales_request": sales_request,
                "periods": list(KpiPeriodsEnum),
                "groupings": list(SalesGroupingsEnum),
                "currencies": list(SalesCurrencyEnum),
                "form_data": form_data,
                "errors": [f"Error updating request: {str(e)}"],
            },
        )


@router.post("/delete/{request_id}")
async def delete_request(request_id: int):
    """Delete a sales report request."""
    try:
        result = default_db.delete_sales_report_request(request_id)
        return RedirectResponse(
            url=f"/?success=Deleted sales report request: {result.name}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?error=Error deleting request: {str(e)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


def validate_form_data(
    period: KpiPeriodsEnum,
    grouping: Optional[SalesGroupingsEnum],
    grouping_value: Optional[str],
    currency: SalesCurrencyEnum,
    recipients: List[RecipientEmail],
) -> List[str]:
    """Validate form data and return list of error messages."""
    errors = []

    # Check grouping/grouping_value relationship
    grouping_value_clean = (grouping_value or "").strip()

    if (grouping is None) != (not grouping_value_clean):
        errors.append(
            "Grouping and grouping value must both be provided or both be empty"
        )

    # Check recipients
    if not recipients:
        errors.append(
            "At least one recipient with both a valid email and name must be provided"
        )
    else:
        for i, rec in enumerate(recipients):
            try:
                # Validate using Pydantic
                RecipientEmail(email=rec.email, name=rec.name)
            except ValidationError as e:
                for error in e.errors():
                    if error["loc"] == ("email",):
                        errors.append(
                            f"Recipient {i + 1}: '{rec.email}' is not a valid email address"
                        )
                    else:
                        errors.append(f"Recipient {i + 1}: {error['msg']}")

    return errors
