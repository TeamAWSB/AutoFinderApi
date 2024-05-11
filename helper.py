class Helper:
    @staticmethod
    def FindVehicleInList(list, vehicle):
        for item in list:
            if item['model'] == vehicle['model']:
                return item
            
        return None