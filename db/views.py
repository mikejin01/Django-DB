from django.shortcuts import render
from .models import Building, Customer
from django.db.models import Q

# Create your views here.
def home(request):
    query = request.GET.get('q')
    tab = request.GET.get('tab', 'buildings')  # default to buildings

    buildings = Building.objects.prefetch_related('services', 'customer').all()
    customers = Customer.objects.all()

    if query:
        # Always filter buildings by BBL (no matter which tab is selected)
        buildings = buildings.filter(
            Q(address__icontains=query) |
            Q(BIN__icontains=query) |
            Q(BBL__icontains=query) |
            Q(customer__first_name__icontains=query) |
            Q(customer__last_name__icontains=query)
        )

        # Only filter customers if the tab is 'customers'
        if tab == 'customers':
            customers = customers.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )

    return render(request, 'home.html', {
        'tab': tab,
        'query': query,
        'buildings': buildings,
        'customers': customers
    })