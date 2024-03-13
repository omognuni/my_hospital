from clinic.models import Doctor
from django.db.models import Q


def filter_doctors(filters):
    doctor_queryset = Doctor.objects.all()
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
            doctor_queryset = doctor_queryset.filter(conditions)

        return doctor_queryset.distinct()
    if time:
        day = time.weekday()
        time = time.time()
        doctor_queryset = doctor_queryset.filter(
            hours__day=day, hours__opening_time__lte=time, hours__closing_time__gte=time
        )
        return doctor_queryset
    return doctor_queryset


def get_doctors(filters=None):
    filters = filters or {}

    doctor_queryset = filter_doctors(filters)

    return doctor_queryset
