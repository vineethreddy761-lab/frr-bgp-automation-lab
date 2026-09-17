package main

import (
    "context"
    "flag"
    "github.com/hashicorp/terraform-plugin-sdk/v2/diag"
    "github.com/hashicorp/terraform-plugin-sdk/v2/helper/schema"
    "github.com/hashicorp/terraform-plugin-sdk/v2/plugin"
)

func Provider() *schema.Provider {
    return &schema.Provider{
        ResourcesMap: map[string]*schema.Resource{
            "mock_network_resource": resourceMockNetwork(),
        },
    }
}

func resourceMockNetwork() *schema.Resource {
    return &schema.Resource{
        CreateContext: resourceMockCreate,
        ReadContext:   resourceMockRead,
        DeleteContext: resourceMockDelete,
        Schema: map[string]*schema.Schema{
            "name": {
                Type:     schema.TypeString,
                Required: true,
                ForceNew: true,
            },
        },
    }
}

func resourceMockCreate(ctx context.Context, d *schema.ResourceData, m interface{}) diag.Diagnostics {
    name := d.Get("name").(string)
    d.SetId(name + "-id")
    return diag.FromErr(nil)
}

func resourceMockRead(ctx context.Context, d *schema.ResourceData, m interface{}) diag.Diagnostics {
    return diag.FromErr(nil)
}

func resourceMockDelete(ctx context.Context, d *schema.ResourceData, m interface{}) diag.Diagnostics {
    d.SetId("")
    return diag.FromErr(nil)
}

func main() {
    var debug bool
    flag.BoolVar(&debug, "debug", false, "set to true to run the provider with support for debuggers")
    flag.Parse()

    plugin.Serve(&plugin.ServeOpts{
        ProviderFunc: Provider,
    })
}
