import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons'; // Expo has built-in icon sets

export default function AppLayout() {
  return (
    <Tabs>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Meal Planner',
          tabBarIcon: ({ color }) => <Ionicons name="restaurant-outline" size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="pantry"
        options={{
          title: 'Digital Pantry',
          tabBarIcon: ({ color }) => <Ionicons name="list-outline" size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'My Profile',
          tabBarIcon: ({ color }) => <Ionicons name="person-outline" size={28} color={color} />,
        }}
      />
      <Tabs.Screen
        name="shoppinglist"
        options={{
          title: 'Shopping List',
          tabBarIcon: ({ color }) => <Ionicons name="cart-outline" size={28} color={color} />,
        }}
      />
    </Tabs>
  );
}