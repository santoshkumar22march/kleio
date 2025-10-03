/**
 * Edit Item Dialog
 * Edit existing inventory item
 */

import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

interface EditItemDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  item: {
    id: number;
    item_name: string;
    category: string;
    quantity: number;
    unit: string;
    expiry_date?: string;
  } | null;
}

const EditItemDialog = ({ open, onOpenChange, item }: EditItemDialogProps) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState({
    quantity: '',
    expiry_date: '',
  });

  useEffect(() => {
    if (item) {
      setFormData({
        quantity: item.quantity.toString(),
        expiry_date: item.expiry_date ? item.expiry_date.split('T')[0] : '',
      });
    }
  }, [item]);

  const updateItemMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.patch(`/api/inventory/${item?.id}/update`, {
        quantity: parseFloat(data.quantity),
        expiry_date: data.expiry_date || null,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      toast({
        title: 'Item Updated!',
        description: 'Item has been updated successfully.',
      });
      onOpenChange(false);
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to Update Item',
        description: error.message || 'Please try again.',
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.quantity) {
      toast({
        title: 'Missing Information',
        description: 'Please enter a quantity.',
        variant: 'destructive',
      });
      return;
    }

    updateItemMutation.mutate(formData);
  };

  if (!item) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Item</DialogTitle>
          <DialogDescription>
            Update quantity and expiry date for {item.item_name}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Item Info (Read-only) */}
          <div className="space-y-2">
            <Label>Item</Label>
            <div className="px-3 py-2 bg-muted rounded-md">
              <p className="font-medium">{item.item_name}</p>
              <p className="text-sm text-muted-foreground">
                Category: {item.category} • Unit: {item.unit}
              </p>
            </div>
          </div>

          {/* Quantity */}
          <div className="space-y-2">
            <Label htmlFor="edit-quantity">Quantity *</Label>
            <Input
              id="edit-quantity"
              type="number"
              step="0.01"
              min="0.01"
              placeholder="1.5"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              disabled={updateItemMutation.isPending}
            />
            <p className="text-xs text-muted-foreground">
              Current: {item.quantity} {item.unit}
            </p>
          </div>

          {/* Expiry Date */}
          <div className="space-y-2">
            <Label htmlFor="edit-expiry">Expiry Date (Optional)</Label>
            <Input
              id="edit-expiry"
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              disabled={updateItemMutation.isPending}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={updateItemMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateItemMutation.isPending}>
              {updateItemMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Item'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EditItemDialog;
