from django.shortcuts import render
from .models import Building
from django.db.models import Q

# Create your views here.
def home(request):
    query = request.GET.get('q')
    buildings = Building.objects.prefetch_related('services', 'customer').all()

    if query:
        buildings = buildings.filter(
            Q(address__icontains=query) |
            Q(BIN__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )
    return render(request, 'home.html', {'buildings': buildings, 'query': query})