/**
 * Enhanced Dashboard Page
 * Central hub with real-time stats, inventory overview, and quick actions
 */

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, Package, Receipt, ChefHat, LogOut, TrendingUp, AlertTriangle, ShoppingCart, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import ReceiptScanner from '@/components/ReceiptScanner';
import InventoryListEnhanced from '@/components/InventoryListEnhanced';
import api from '@/lib/api';

interface InventoryItem {
  id: number;
  item_name: string;
  category: string;
  quantity: number;
  unit: string;
  status: string;
  added_date: string;
  expiry_date?: string;
}

const DashboardEnhanced = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('inventory');

  // Fetch inventory for stats (only active items)
  const { data: items } = useQuery<InventoryItem[]>({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await api.get('/api/inventory/list', {
        params: { status_filter: 'active' }
      });
      return response.data;
    },
  });

  // Calculate stats
  const stats = useMemo(() => {
    if (!items) return { total: 0, lowStock: 0, expiringSoon: 0, categories: 0 };

    const total = items.length;
    
    // Low stock: items with quantity <= 1 or less than 100g/ml
    const lowStock = items.filter(item => {
      if (item.unit === 'kg' || item.unit === 'liters') {
        return item.quantity <= 0.5;
      } else if (item.unit === 'grams' || item.unit === 'ml') {
        return item.quantity <= 100;
      } else {
        return item.quantity <= 1;
      }
    }).length;

    // Expiring soon: items expiring within 7 days
    const expiringSoon = items.filter(item => {
      if (!item.expiry_date) return false;
      const daysUntilExpiry = Math.ceil(
        (new Date(item.expiry_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
      );
      return daysUntilExpiry >= 0 && daysUntilExpiry <= 7;
    }).length;

    // Unique categories
    const categories = new Set(items.map(item => item.category)).size;

    return { total, lowStock, expiringSoon, categories };
  }, [items]);

  const handleSignOut = async () => {
    try {
      await signOut();
      toast({
        title: 'Signed Out',
        description: 'You have been successfully signed out.',
      });
      navigate('/');
    } catch (error) {
      toast({
        title: 'Sign Out Failed',
        description: 'An error occurred while signing out.',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-lg sticky top-0 z-40 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg gradient-hero flex items-center justify-center shadow-md">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary">Kleio.ai</h1>
                <p className="text-xs text-muted-foreground">Smart Inventory</p>
              </div>
            </div>

            {/* User Info & Actions */}
            <div className="flex items-center gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">{user?.email}</p>
                <p className="text-xs text-muted-foreground">Welcome back!</p>
              </div>
              <Button variant="outline" size="sm" onClick={handleSignOut}>
                <LogOut className="w-4 h-4 sm:mr-2" />
                <span className="hidden sm:inline">Sign Out</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-xs sm:text-sm">Total Items</CardDescription>
                <Package className="w-4 h-4 text-primary" />
              </div>
              <CardTitle className="text-2xl sm:text-3xl">{stats.total}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {stats.categories} categories
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-xs sm:text-sm">Low Stock</CardDescription>
                <AlertTriangle className="w-4 h-4 text-orange-600" />
              </div>
              <CardTitle className="text-2xl sm:text-3xl">{stats.lowStock}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {stats.lowStock > 0 ? 'Need restocking' : 'All good!'}
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-xs sm:text-sm">Expiring Soon</CardDescription>
                <Calendar className="w-4 h-4 text-red-600" />
              </div>
              <CardTitle className="text-2xl sm:text-3xl">{stats.expiringSoon}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {stats.expiringSoon > 0 ? 'Within 7 days' : 'None expiring'}
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardDescription className="text-xs sm:text-sm">Recipes</CardDescription>
                <ChefHat className="w-4 h-4 text-green-600" />
              </div>
              <CardTitle className="text-2xl sm:text-3xl">
                {stats.total > 0 ? '∞' : '0'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                {stats.total > 0 ? 'AI-generated' : 'Add items first'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
            <TabsTrigger value="inventory" className="text-xs sm:text-sm">
              <Package className="w-4 h-4 mr-1 sm:mr-2" />
              <span>Inventory</span>
            </TabsTrigger>
            <TabsTrigger value="scan-receipt" className="text-xs sm:text-sm">
              <Receipt className="w-4 h-4 mr-1 sm:mr-2" />
              <span>Scan Receipt</span>
            </TabsTrigger>
            <TabsTrigger value="recipes" className="text-xs sm:text-sm">
              <ChefHat className="w-4 h-4 mr-1 sm:mr-2" />
              <span>Recipes</span>
            </TabsTrigger>
          </TabsList>

          {/* Inventory Tab */}
          <TabsContent value="inventory" className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl sm:text-2xl font-bold">Your Inventory</h2>
                <p className="text-sm text-muted-foreground">Manage your household items</p>
              </div>
            </div>
            <InventoryListEnhanced />
          </TabsContent>

          {/* Scan Receipt Tab */}
          <TabsContent value="scan-receipt" className="space-y-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold">Scan Receipt</h2>
              <p className="text-sm text-muted-foreground">Upload a photo to extract items automatically</p>
            </div>
            <ReceiptScanner onSuccess={() => setActiveTab('inventory')} />
          </TabsContent>

          {/* Recipes Tab */}
          <TabsContent value="recipes" className="space-y-4">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold">Recipe Suggestions</h2>
              <p className="text-sm text-muted-foreground">AI-powered recipes based on your inventory</p>
            </div>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <ChefHat className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Coming Soon!</h3>
                  <p className="text-muted-foreground mb-4">
                    Recipe suggestions will appear here once you add items to your inventory.
                  </p>
                  {stats.total === 0 && (
                    <Button onClick={() => setActiveTab('scan-receipt')}>
                      <Receipt className="w-4 h-4 mr-2" />
                      Scan Your First Receipt
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default DashboardEnhanced;
