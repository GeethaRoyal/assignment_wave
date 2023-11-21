from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from common.enums import BillingStatus, PaymentStatus
from core.models import BillingHistory, TableNo, Allotment, Manager
from common.permissions import IsManagerOrReadOnly, IsManager, IsAdminOrReadOnly
from manager.serializers import ManagerSerializer, BillingHistorySerializer, TableNoSerializer, TableNoListSerializer


# Create your views here.
class BillingHistoryViewSet(viewsets.ModelViewSet):
    queryset = BillingHistory.objects.filter(is_removed=False)
    serializer_class = BillingHistorySerializer
    permission_classes = [IsManagerOrReadOnly]

    def list(self, request, *args, **kwargs):
        paginator = CustomPagination()
        tables = BillingHistory.objects.all()
        result_page = paginator.paginate_queryset(tables, request)
        serializer = BillingHistorySerializer(result_page, many=True)

        response_data = {
            'billing_history': serializer.data,
            'pagination': {
                'total_pages': paginator.page.paginator.num_pages,
                'current_page': paginator.page.number,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }
        }

        return Response(response_data)

    @action(detail=False, methods=['GET'], url_path="live")
    def live_billing_history(self, request):
        payload = BillingHistory.objects.filter(
            status=BillingStatus.PENDING.value, payment_status=PaymentStatus.UNPAID.value)
        return Response({"payload": payload})


class TableNoViewSet(viewsets.ModelViewSet):
    queryset = TableNo.objects.filter(is_removed=False)
    serializer_class = TableNoListSerializer
    permission_classes = [IsManagerOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = TableNoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Done"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def remove_table(self, request):
        table_no = request.data.get('table_no', None)
        if not table_no:
            return Response({"message": "Table number parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            table_obj = (TableNo.objects.filter(table_no=table_no, is_removed=False))
            restaurant_id = table_obj.restaurant_id
            table_obj.delete()
            Allotment.objects.filter(table_no=table_no, restaurant_id=restaurant_id).delete()
            return Response({"message": "Done"})
        except TableNo.DoesNotExist:
            return Response({"message": "Table not found"}, status=status.HTTP_404_NOT_FOUND)


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.filter(is_removed=False)
    serializer_class = ManagerSerializer
    permission_classes = [IsManager, IsAdminOrReadOnly]


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
