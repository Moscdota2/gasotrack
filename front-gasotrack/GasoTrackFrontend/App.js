import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, FlatList } from 'react-native';

const App = () => {
  const [estaciones, setEstaciones] = useState([]);

  useEffect(() => {
    // Realizar la solicitud a la API al cargar el componente
    fetch('http://localhost:5000/estaciones-get') // Asegúrate de que tu API Flask esté corriendo en el puerto 5000
      .then(response => response.json())
      .then(data => setEstaciones(data))
      .catch(error => console.error('Error al obtener datos de la API:', error));
  }, []);

  const renderItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.nombre}>{item.nombre}</Text>
      <Text style={styles.direccion}>{item.direccion}</Text>
      <Text style={styles.tipo}>Tipo: {item.tipo}</Text>
      <Text style={styles.combustibles}>Combustibles: {item.combustibles.join(', ')}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={estaciones}
        renderItem={renderItem}
        keyExtractor={item => item.id.toString()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  item: {
    backgroundColor: '#f9c2ff',
    padding: 20,
    marginVertical: 8,
    borderRadius: 5,
  },
  nombre: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  direccion: {
    fontSize: 14,
    color: 'gray',
  },
  tipo: {
    fontSize: 14,
    marginTop: 5,
  },
  combustibles: {
    fontSize: 14,
    marginTop: 5,
  },
});

export default App;