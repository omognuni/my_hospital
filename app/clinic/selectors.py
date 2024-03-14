from clinic.enums import RequestStatus
from clinic.models import Doctor, TreatmentRequest
from django.db.models import Q


def filter_doctors(filters):
    doctor_queryset = (
        Doctor.objects.select_related("hospital")
        .prefetch_related("hours", "departments", "treatments")
        .all()
    )
    search = filters.get("search", None)
    time = filters.get("time", None)
    if search:
        search_keywords = search.split(" ")
        for keyword in search_keywords:
            conditions = (
                Q(name__icontains=keyword)
                | Q(hospital__name__icontains=keyword)
                | Q(departments__name__icontains=keyword)
                | Q(treatments__name__icontains=keyword)
            )
            doctor_queryset = doctor_queryset.filter(conditions).distinct()

    if time:
        day = time.weekday()
        time = time.time()
        doctor_queryset = doctor_queryset.filter(
            hours__day=day, hours__opening_time__lte=time, hours__closing_time__gte=time
        )

    return doctor_queryset


def filter_requests(filters):
    doctor_id = filters.get("doctor_id", None)

    request_queryset = TreatmentRequest.objects.select_related("patient").all()
    if doctor_id:
        request_queryset = request_queryset.filter(doctor_id=doctor_id).exclude(
            status=RequestStatus.ACCEPTED
        )
    return request_queryset


def get_doctors(filters=None):
    filters = filters or {}

    doctor_queryset = filter_doctors(filters)

    return doctor_queryset


def get_requests(filters=None):
    filters = filters or {}

    request_queryset = filter_requests(filters)

    return request_queryset
