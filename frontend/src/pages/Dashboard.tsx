/**
 * Main Dashboard Page
 * Central hub with inventory overview and quick actions
 */

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, Package, Receipt, ChefHat, LogOut, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import ReceiptScanner from '@/components/ReceiptScanner';
import InventoryList from '@/components/InventoryList';

const Dashboard = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('inventory');

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
      <header className="border-b bg-background/80 backdrop-blur-lg sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg gradient-hero flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary">Kleio.ai</h1>
                <p className="text-xs text-muted-foreground">Smart Inventory</p>
              </div>
            </div>

            {/* User Info & Actions */}
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium">{user?.email}</p>
                <p className="text-xs text-muted-foreground">Welcome back!</p>
              </div>
              <Button variant="outline" size="sm" onClick={handleSignOut}>
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total Items</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                <Package className="w-3 h-3 inline mr-1" />
                Track your inventory
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Low Stock</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                <span className="inline-flex items-center">
                  Items running low
                </span>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Recipes Available</CardDescription>
              <CardTitle className="text-3xl">-</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                <ChefHat className="w-3 h-3 inline mr-1" />
                Based on inventory
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-grid">
            <TabsTrigger value="inventory">
              <Package className="w-4 h-4 mr-2" />
              Inventory
            </TabsTrigger>
            <TabsTrigger value="scan-receipt">
              <Receipt className="w-4 h-4 mr-2" />
              Scan Receipt
            </TabsTrigger>
            <TabsTrigger value="recipes">
              <ChefHat className="w-4 h-4 mr-2" />
              Recipes
            </TabsTrigger>
          </TabsList>

          {/* Inventory Tab */}
          <TabsContent value="inventory" className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Your Inventory</h2>
                <p className="text-muted-foreground">Manage your household items</p>
              </div>
              <Button onClick={() => setActiveTab('scan-receipt')}>
                <Plus className="w-4 h-4 mr-2" />
                Add Items
              </Button>
            </div>
            <InventoryList />
          </TabsContent>

          {/* Scan Receipt Tab */}
          <TabsContent value="scan-receipt" className="space-y-4">
            <div>
              <h2 className="text-2xl font-bold">Scan Receipt</h2>
              <p className="text-muted-foreground">Upload a photo to extract items automatically</p>
            </div>
            <ReceiptScanner onSuccess={() => setActiveTab('inventory')} />
          </TabsContent>

          {/* Recipes Tab */}
          <TabsContent value="recipes" className="space-y-4">
            <div>
              <h2 className="text-2xl font-bold">Recipe Suggestions</h2>
              <p className="text-muted-foreground">AI-powered recipes based on your inventory</p>
            </div>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <ChefHat className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Coming Soon!</h3>
                  <p className="text-muted-foreground">
                    Recipe suggestions will appear here once you add items to your inventory.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
