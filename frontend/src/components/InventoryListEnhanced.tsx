/**
 * Enhanced Inventory List Component
 * Display and manage inventory with search, filter, sort, bulk actions
 */

import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Package, Trash2, AlertCircle, Edit2, Search, Filter, SortAsc, Plus, X, TrendingUp, Clock } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';
import { format } from 'date-fns';
import AddItemDialog from './AddItemDialog';
import EditItemDialog from './EditItemDialog';

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

interface PatternPrediction {
  item_name: string;
  category: string;
  urgency: string;
  confidence_level: string;
  days_until_depletion: number | null;
  avg_days_between_purchases: number | null;
}

const InventoryListEnhanced = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'quantity'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);

  // Fetch inventory (only active items)
  const { data: items, isLoading, error } = useQuery<InventoryItem[]>({
    queryKey: ['inventory'],
    queryFn: async () => {
      const response = await api.get('/api/inventory/list', {
        params: { status_filter: 'active' }
      });
      return response.data;
    },
  });

  // Fetch pattern predictions
  const { data: predictions } = useQuery<PatternPrediction[]>({
    queryKey: ['all-predictions'],
    queryFn: async () => {
      const response = await api.get('/api/shopping/predictions');
      return response.data;
    },
  });

  // Create a map of item predictions for quick lookup
  const predictionMap = useMemo(() => {
    if (!predictions) return new Map();
    return new Map(predictions.map(p => [p.item_name.toLowerCase(), p]));
  }, [predictions]);

  // Delete single item
  const deleteItemMutation = useMutation({
    mutationFn: async (itemId: number) => {
      await api.delete(`/api/inventory/${itemId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast({
        title: 'Item Removed',
        description: 'Item has been removed from your inventory.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Delete Failed',
        description: error.message || 'Failed to remove item.',
        variant: 'destructive',
      });
    },
  });

  // Bulk delete
  const bulkDeleteMutation = useMutation({
    mutationFn: async (itemIds: number[]) => {
      await Promise.all(itemIds.map(id => api.delete(`/api/inventory/${id}`)));
    },
    onSuccess: (_, itemIds) => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      setSelectedItems([]);
      toast({
        title: 'Items Removed',
        description: `Successfully removed ${itemIds.length} items.`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Bulk Delete Failed',
        description: error.message || 'Failed to remove items.',
        variant: 'destructive',
      });
    },
  });

  // Filter, search, and sort
  const filteredAndSortedItems = useMemo(() => {
    if (!items) return [];

    let result = [...items];

    // Search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(item =>
        item.item_name.toLowerCase().includes(query) ||
        item.category.toLowerCase().includes(query)
      );
    }

    // Filter by category
    if (categoryFilter && categoryFilter !== 'all') {
      result = result.filter(item => item.category.toLowerCase() === categoryFilter);
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      
      if (sortBy === 'name') {
        comparison = a.item_name.localeCompare(b.item_name);
      } else if (sortBy === 'date') {
        comparison = new Date(a.added_date).getTime() - new Date(b.added_date).getTime();
      } else if (sortBy === 'quantity') {
        comparison = a.quantity - b.quantity;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [items, searchQuery, categoryFilter, sortBy, sortOrder]);

  // Get unique categories
  const categories = useMemo(() => {
    if (!items) return [];
    const cats = new Set(items.map(item => item.category));
    return Array.from(cats).sort();
  }, [items]);

  // Handlers
  const handleDelete = (itemId: number, itemName: string) => {
    if (confirm(`Remove "${itemName}" from inventory?`)) {
      deleteItemMutation.mutate(itemId);
    }
  };

  const handleBulkDelete = () => {
    if (selectedItems.length === 0) return;
    if (confirm(`Remove ${selectedItems.length} selected items?`)) {
      bulkDeleteMutation.mutate(selectedItems);
    }
  };

  const handleEdit = (item: InventoryItem) => {
    setEditingItem(item);
    setEditDialogOpen(true);
  };

  const toggleSelectItem = (itemId: number) => {
    setSelectedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedItems.length === filteredAndSortedItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(filteredAndSortedItems.map(item => item.id));
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'grains': 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100',
      'dairy': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
      'vegetables': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      'fruits': 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-100',
      'spices': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100',
      'oils': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
      'snacks': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100',
      'beverages': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-100',
    };
    return colors[category.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100';
  };

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case 'urgent':
        return <Badge variant="destructive" className="text-xs">🚨 URGENT</Badge>;
      case 'this_week':
        return <Badge className="bg-orange-500 hover:bg-orange-600 text-white text-xs">📅 THIS WEEK</Badge>;
      case 'later':
        return <Badge variant="secondary" className="text-xs">✅ GOOD</Badge>;
      default:
        return null;
    }
  };

  const getConfidenceStars = (confidence: string) => {
    switch (confidence) {
      case 'high': return '⭐⭐⭐';
      case 'medium': return '⭐⭐';
      case 'low': return '⭐';
      default: return '';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 mx-auto text-destructive mb-4" />
            <h3 className="text-lg font-semibold mb-2">Failed to Load Inventory</h3>
            <p className="text-sm text-muted-foreground">
              {(error as any).message || 'Please try again later.'}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!items || items.length === 0) {
    return (
      <>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Package className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Items Yet</h3>
              <p className="text-sm text-muted-foreground mb-6">
                Start by scanning a receipt or adding items manually
              </p>
              <Button onClick={() => setAddDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Item
              </Button>
            </div>
          </CardContent>
        </Card>
        <AddItemDialog open={addDialogOpen} onOpenChange={setAddDialogOpen} />
      </>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <CardTitle className="text-xl">Inventory Items</CardTitle>
            <Button onClick={() => setAddDialogOpen(true)} size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add Item
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Search & Filters */}
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search items..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0"
                  onClick={() => setSearchQuery('')}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>

            {/* Category Filter */}
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat.toLowerCase()}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
              <SelectTrigger className="w-full sm:w-[150px]">
                <SortAsc className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Date Added</SelectItem>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="quantity">Quantity</SelectItem>
              </SelectContent>
            </Select>

            {/* Sort Order */}
            <Button
              variant="outline"
              size="icon"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            >
              <SortAsc className={`w-4 h-4 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
            </Button>
          </div>

          {/* Bulk Actions */}
          {selectedItems.length > 0 && (
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <span className="text-sm font-medium">
                {selectedItems.length} item{selectedItems.length !== 1 ? 's' : ''} selected
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedItems([])}
                >
                  Clear
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleBulkDelete}
                  disabled={bulkDeleteMutation.isPending}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Selected
                </Button>
              </div>
            </div>
          )}

          {/* Results Count */}
          <div className="text-sm text-muted-foreground">
            Showing {filteredAndSortedItems.length} of {items.length} items
          </div>

          {/* Table */}
          <div className="border rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <Checkbox
                        checked={selectedItems.length === filteredAndSortedItems.length && filteredAndSortedItems.length > 0}
                        onCheckedChange={toggleSelectAll}
                      />
                    </TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Quantity</TableHead>
                    <TableHead className="hidden lg:table-cell">Pattern Status</TableHead>
                    <TableHead className="hidden sm:table-cell">Added</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedItems.map((item) => {
                    const pattern = predictionMap.get(item.item_name.toLowerCase());
                    return (
                      <TableRow key={item.id}>
                        <TableCell>
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onCheckedChange={() => toggleSelectItem(item.id)}
                          />
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{item.item_name}</span>
                              {pattern && getUrgencyBadge(pattern.urgency)}
                            </div>
                            {/* Mobile: Show pattern info */}
                            {pattern && (
                              <div className="lg:hidden text-xs text-muted-foreground flex items-center gap-2">
                                {pattern.days_until_depletion !== null && (
                                  <span className="flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    {Math.round(pattern.days_until_depletion)}d left
                                  </span>
                                )}
                                {pattern.avg_days_between_purchases && (
                                  <span className="flex items-center gap-1">
                                    <TrendingUp className="w-3 h-3" />
                                    ~{Math.round(pattern.avg_days_between_purchases)}d cycle
                                  </span>
                                )}
                                <span>{getConfidenceStars(pattern.confidence_level)}</span>
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={getCategoryColor(item.category)} variant="secondary">
                            {item.category}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex flex-col items-end">
                            <span className="font-medium">{item.quantity} {item.unit}</span>
                            {pattern && pattern.days_until_depletion !== null && (
                              <div className="w-full max-w-[80px] mt-1">
                                <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                  <div 
                                    className={`h-full transition-all ${
                                      pattern.days_until_depletion <= 1 ? 'bg-red-500' :
                                      pattern.days_until_depletion <= 7 ? 'bg-orange-500' :
                                      'bg-green-500'
                                    }`}
                                    style={{ 
                                      width: `${Math.min(100, Math.max(0, (pattern.days_until_depletion / (pattern.avg_days_between_purchases || 7)) * 100))}%`
                                    }}
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        </TableCell>
                        {/* Desktop: Pattern Status Column */}
                        <TableCell className="hidden lg:table-cell">
                          {pattern ? (
                            <div className="text-xs space-y-1">
                              {pattern.days_until_depletion !== null && (
                                <div className="flex items-center gap-1 text-muted-foreground">
                                  <Clock className="w-3 h-3" />
                                  Runs out in {Math.round(pattern.days_until_depletion)} day{Math.round(pattern.days_until_depletion) !== 1 ? 's' : ''}
                                </div>
                              )}
                              {pattern.avg_days_between_purchases && (
                                <div className="flex items-center gap-1 text-muted-foreground">
                                  <TrendingUp className="w-3 h-3" />
                                  Buy every ~{Math.round(pattern.avg_days_between_purchases)} days
                                </div>
                              )}
                              <div className="flex items-center gap-1">
                                <span className="text-muted-foreground">{getConfidenceStars(pattern.confidence_level)}</span>
                                <span className="capitalize text-muted-foreground">{pattern.confidence_level}</span>
                              </div>
                            </div>
                          ) : (
                            <span className="text-xs text-muted-foreground">Building pattern...</span>
                          )}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground hidden sm:table-cell">
                          {format(new Date(item.added_date), 'MMM d, yyyy')}
                        </TableCell>
                        <TableCell>
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(item)}
                            >
                              <Edit2 className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(item.id, item.item_name)}
                              disabled={deleteItemMutation.isPending}
                            >
                              <Trash2 className="w-4 h-4 text-destructive" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dialogs */}
      <AddItemDialog open={addDialogOpen} onOpenChange={setAddDialogOpen} />
      <EditItemDialog 
        open={editDialogOpen} 
        onOpenChange={setEditDialogOpen} 
        item={editingItem}
      />
    </>
  );
};

export default InventoryListEnhanced;
