from django.shortcuts import render
from .models import Building, Client
from django.db.models import Q

# Create your views here.
def home(request):
    query = request.GET.get('q')
    tab = request.GET.get('tab', 'buildings')  # default to buildings

    buildings = Building.objects.prefetch_related('services', 'client').all()
    clients = Client.objects.all()

    if query:
        # Always filter buildings by BBL (no matter which tab is selected)
        buildings = buildings.filter(
            Q(address__icontains=query) |
            Q(BIN__icontains=query) |
            Q(BBL__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query)
        )

        # Only filter clients if the tab is 'clients'
        if tab == 'clients':
            clients = clients.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )

    return render(request, 'home.html', {
        'tab': tab,
        'query': query,
        'buildings': buildings,
        'clients': clients
    })