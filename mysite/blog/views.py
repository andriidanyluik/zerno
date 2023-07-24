from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.http import HttpResponse
import folium
from folium.plugins import MarkerCluster, LocateControl, Fullscreen
from branca.element import Figure
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect
import requests
from .models import Cities_maps, Tariff
from .forms import SearchRoute
from geopy.geocoders import Nominatim
from decimal import Decimal

def build_route(city_from, city_to):
    osrm_url = "https://router.project-osrm.org/route/v1/driving/{},{};{},{}?steps=true&alternatives=true&geometries=geojson&overview=full".format(
        city_from[1], city_from[0], city_to[1], city_to[0]
    )
    
    response = requests.get(osrm_url)
    data = response.json()

    if 'routes' in data and len(data['routes']) > 0:
        route = data['routes'][0]
        route_coordinates = []
        for point in route['geometry']['coordinates']:
            route_coordinates.append([point[1], point[0]])
            distance = route['distance']  # Отримуємо відстань з відповіді
        return route_coordinates, distance

    return None, None

def get_coordinates_by_city_name(city_name):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


def map_calculating(request):
    form = SearchRoute(request.POST or None)
    city_btn = Cities_maps.objects.all()
    city_from = None
    city_to = None
    route_coordinates = None
    distance = None
    city_from = Cities_maps.objects.values('city_name_client').distinct().order_by('city_name_client')
    city_btn = []
    
    for x in city_from:
        if x['city_name_client'] != None:
            city_btn.append((x['city_name_client']))
    city_from_name = None

    city_to = Cities_maps.objects.values('city_name_product').distinct().order_by('city_name_product')
    city_btn2 = []
    for x in city_to:
        if x['city_name_product'] != None:
            city_btn2.append((x['city_name_product']))
    city_to_name = None
    if request.method == 'POST':
        
        if form.is_valid():
            city_from_name = form.cleaned_data['city_from']
            request.session['city_from_name'] = city_from_name
            city_to_names = form.cleaned_data['city_to']
            city_to_list = list(city_to_names)
            list_routes = []
            city_from_lat, city_from_lon = get_coordinates_by_city_name(city_from_name)

            if city_from_lat:
                city_from_coor = (city_from_lat, city_from_lon)

                for city_to_name in city_to_list:
                    city_to_lat, city_to_lon = get_coordinates_by_city_name(city_to_name)
                    
                    if city_to_lat:
                        city_to_coor = (city_to_lat, city_to_lon)
                        route_coordinates, distance = build_route(city_from_coor, city_to_coor)

                        if route_coordinates:
                            list_routes.append({
                                'city_to_name': city_to_name,
                                'route_coordinates': route_coordinates,
                                'distance': distance//1000,
                                'city_to_coor': city_to_coor,
                            })
            fig = Figure(height=450)
            m = folium.Map(location=city_from_coor, zoom_start=5, width="100%",
                 )
            marker_cluster = MarkerCluster().add_to(m)
            tooltip = "Натисніть ТУТ"
            if city_from:
                folium.Marker(location=city_from_coor, popup=city_from_name,tooltip = tooltip, icon=folium.Icon(color='blue', icon="fa-solid fa-a", prefix='fa')).add_to(m)
            list_routes_table=[]
            for route in list_routes:
                city_to_name = route['city_to_name']
                route_coordinates = route['route_coordinates']
                distance = route['distance']
                city_to_coor = route['city_to_coor']
                if route_coordinates:
                    print(city_to_coor)
                    link = f'<a href="http://127.0.0.1:8000/city/{city_to_name}" target="_blank">Посилання</a>'
                    links = f"http://127.0.0.1:8000/city/{city_to_name}"
                    iframe = '<h3>' + str(city_to_name)  + '</h3>' + '<p>' + 'Дистанція: ' + str(distance) + "</p>" + '<p>' + "Посилання на маршут: " + link + '<p>'
                    iframe = folium.IFrame(iframe)
                    popup = folium.Popup(iframe, min_width=250, max_width=350)
                    folium.Marker(location=city_from_coor, popup="Місто відправки", icon=folium.Icon(color='blue', icon="fa-solid fa-a", prefix='fa')).add_to(m)
                    marker_cluster.add_child(folium.Marker(location=city_to_coor, popup=popup, icon=folium.Icon(color='blue',icon="fa-solid fa-truck", prefix='fa'))).add_to(m)
                    #folium.PolyLine(locations=route_coordinates,color='#28D6EE').add_to(m)
                    list_routes_table.append({"city_to_name": city_to_name,
                                              "links": links,
                                              "distance":distance
                                              })
            LocateControl().add_to(m)
            Fullscreen().add_to(m)
            my_map = m._repr_html_()
            draw_map = True
            table_routes=True
            return render(request, 'blog/map/map_shelter.html', {
                'draw_map': draw_map,
                "city_from_name": city_from_name,
                "city_to_names": city_to_names,
                'my_map': my_map,
                'list_routes': list_routes,
                'city_btn': city_btn,
                'city_btn2': city_btn2,
                'form': form,
                'list_routes_table':list_routes_table,
                'table_routes':table_routes,
            })


    table_routes = False
    m2 = folium.Map([49.5011, 23.5842], zoom_start=5,  attr='"Zernovoz"')
    LocateControl().add_to(m2)
    Fullscreen().add_to((m2))                                               
    fig = Figure(height=550)
    m2 = m2._repr_html_()
    draw_map = True
    return render(request, 'blog/map/map_shelter.html', {'draw_map': draw_map,
                                                        'my_map': m2,
                                                        'distance': distance,
                                                        'city_btn': city_btn, 
                                                        'city_btn2': city_btn2,
                                                        'form': form,
                                                        'table_routes':table_routes,
                                                        })
def print_city(request, city_name):
    city_from_name = request.session['city_from_name']
    city_from_lat, city_from_lon = get_coordinates_by_city_name(city_from_name)
    city_to_lat, city_to_lon = get_coordinates_by_city_name(city_name)

    # Побудувати маршрут і отримати координати маршруту
    city_from_coor = (city_from_lat, city_from_lon)
    city_to_coor = (city_to_lat, city_to_lon)
    route_coordinates, distance = build_route(city_from_coor, city_to_coor)

    m = folium.Map(location=city_from_coor, zoom_start=7)

    if city_from_coor:
        folium.Marker(location=city_from_coor, popup=city_from_name, icon=folium.Icon(color='green')).add_to(m)
    if city_to_coor:
        folium.Marker(location=city_to_coor, popup=city_name, icon=folium.Icon(color='red')).add_to(m)

    if route_coordinates:
        folium.PolyLine(locations=route_coordinates, color='#2AD3F5').add_to(m)
    LocateControl().add_to(m)
    Fullscreen().add_to((m)) 
    my_map = m._repr_html_()
    distance = distance//1000
    cost = calculate_tariff(distance)

    return render(request, 'blog/map/map_with_route.html', {"city_name_to": city_name,
                                                             "city_from_name": city_from_name,
                                                             'my_map': my_map,
                                                             'distance': distance,
                                                             'cost': cost,
                                                             })

def map_detail(request):
    form = SearchRoute(request.POST or None)
    city_btn = Cities_maps.objects.all()
    city_from = None
    city_to = None
    route_coordinates = None
    distance = None
    city_from = Cities_maps.objects.values('city_name_client').distinct().order_by('city_name_client')
    city_btn = []
    
    for x in city_from:
        if x['city_name_client'] != None:
            city_btn.append((x['city_name_client']))
    city_from_name = None

    city_to = Cities_maps.objects.values('city_name_product').distinct().order_by('city_name_product')
    city_btn2 = []
    for x in city_to:
        if x['city_name_product'] != None:
            city_btn2.append((x['city_name_product']))
    city_to_name = None

    if request.method == 'POST':
        if form.is_valid():
            city_from_name = form.cleaned_data['city_from']
            city_to_names = form.cleaned_data['city_to']
            city_to_list = list(city_to_names)
            list_routes = []
            city_from_lat, city_from_lon = get_coordinates_by_city_name(city_from_name)

            if city_from_lat:
                city_from_coor = (city_from_lat, city_from_lon)

                for city_to_name in city_to_list:
                    city_to_lat, city_to_lon = get_coordinates_by_city_name(city_to_name)

                    if city_to_lat:
                        city_to_coor = (city_to_lat, city_to_lon)
                        route_coordinates, distance = build_route(city_from_coor, city_to_coor)

                        if route_coordinates:
                            list_routes.append({
                                'city_to_name': city_to_name,
                                'route_coordinates': route_coordinates,
                                'distance': distance,
                            })

            m = folium.Map(location=city_from_coor, zoom_start=10)

            if city_from:
                folium.Marker(location=city_from_coor, popup=city_from_name, icon=folium.Icon(color='green')).add_to(m)

            for route in list_routes:
                city_to_name = route['city_to_name']
                route_coordinates = route['route_coordinates']
                distance = route['distance']

                if route_coordinates:
                    folium.Marker(location=city_to_coor, popup=city_to_name, icon=folium.Icon(color='red')).add_to(m)
                    folium.PolyLine(locations=route_coordinates,color='#28D6EE').add_to(m)

            LocateControl().add_to(m)
            Fullscreen().add_to(m)
            my_map = m._repr_html_()
            draw_map = True
            calculate = True

            return render(request, 'blog/map/map_shelter.html', {
                'draw_map': draw_map,
                "city_from_name": city_from_name,
                "city_to_names": city_to_names,
                'my_map': my_map,
                'list_routes': list_routes,
                'city_btn': city_btn,
                'city_btn2': city_btn2,
                'form': form,
                'calculate': calculate,
            })

    m2 = folium.Map([49.5011, 23.5842], zoom_start=8,  attr='"Zernovoz"')
    LocateControl().add_to(m2)
    Fullscreen().add_to((m2))                                               
    fig = Figure(height=550)
    m2 = m2._repr_html_()
    draw_map = True
    calculate = False
    return render(request, 'blog/map/map_shelter.html', {'draw_map': draw_map,
                                                        'my_map': m2,
                                                        'distance': distance,
                                                        'city_btn': city_btn, 
                                                        'city_btn2': city_btn2,
                                                        'form': form,
                                                        'calculate': calculate,})

def calculate_tariff(distance):
    # Отримуємо всі тарифи, впорядковані за зростанням початкового кілометражу
    tariffs = Tariff.objects.order_by('start_distance')

    total_cost = Decimal('0')
    remaining_distance = Decimal(str(distance))

    # Оброблюємо кожний діапазон окремо
    for tariff in tariffs:
        if remaining_distance <= 0:
            break

        # Визначаємо, скільки кілометрів можна обробити за поточний тариф
        distance_in_tariff = min(remaining_distance, tariff.end_distance - tariff.start_distance + 1)

        # Додаємо вартість тарифу для поточного діапазону
        total_cost += distance_in_tariff * tariff.price

        # Оновлюємо залишкову відстань, яку ще потрібно обробити
        remaining_distance -= distance_in_tariff

    return total_cost