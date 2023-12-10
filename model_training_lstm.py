# %%
import pandas as pd
from glob import glob
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
import seaborn as sns

_ = torch.manual_seed(1)

# %%
pre_df = pd.read_csv(
    glob("data/*")[-1],
    # index_col=0,
    parse_dates=True,
).loc[:, ["MEASUREMENT_CD_OMSCHRIJVING", "MEETWAARDE", "DT_MEETWAARDE"]]
# %%
df = (
    pre_df.pivot_table(
        index="DT_MEETWAARDE",
        columns="MEASUREMENT_CD_OMSCHRIJVING",
        values="MEETWAARDE",
    )
    .reset_index()
    .rename(
        columns={
            "DT_MEETWAARDE": "timestamp",
            "Avg. voltage L1 (V)": "l1",
            "Avg. voltage L2 (V)": "l2",
            "Avg. voltage L3 (V)": "l3",
        }
    )
    .loc[:, ["timestamp", "l1", "l2", "l3"]]
    .assign(
        **{
            "timestamp": lambda x: pd.to_datetime(
                x["timestamp"], format="%d/%m/%Y %H:%M"
            ),
        }
    )
    .dropna(axis="index")
    .set_index("timestamp")
    # normalize data frame df with mean of 0 and variance of 1
    # .apply(lambda x: (x - x.mean()) / x.std())
    # min max normalize
    # .apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    .reset_index()
)
df.columns.name = None

# %%
lstm = nn.LSTM(input_size=3, hidden_size=3,
               num_layers=1, batch_first=True)  # Input dim is 3, output dim is 3
inputs = [torch.randn(1, 3) for _ in range(5)]  # make a sequence of length 5
inputs = torch.cat(inputs).view(len(inputs), 1, -1)
# initialize the hidden state.
hidden = (torch.randn(1, 5, 3), torch.randn(1, 5, 3))  # clean out hidden state
# hidden = (torch.randn(1, 1, 3) + 230, torch.randn(1, 1, 3) + 230)  # clean out hidden state
out, hidden = lstm(inputs, hidden)
# %%
[torch.randn(1, 3) for _ in range(5)]
# %%
# put the l1, l2, l3 in a list of tensors
inputs = [
    torch.tensor([x], dtype=torch.float32) for x in df.loc[:, ["l1", "l2", "l3"]].values
]
inputs = torch.cat(inputs).view(len(inputs), 1, -1)
# %%
# normalize inputs using mean 0 and variance 1
normalized_inputs = (inputs - inputs.mean(dim=0)) / inputs.std(dim=0)

# %%
# inverse the normalization
normalized_inputs * inputs.std(dim=0) + inputs.mean(dim=0)

# %%
hidden = (torch.randn(1, 864, 3), torch.randn(1, 864, 3))  # clean out hidden state
out, hidden = lstm(normalized_inputs, hidden)
out

# %%
# inverse output normalization
inverse_norm_out = out * inputs.std(dim=0) + inputs.mean(dim=0)

# %%
# convert out to a dataframe
output_df = pd.DataFrame(
    inverse_norm_out.detach().numpy().reshape(-1, 3),
    columns=["l1", "l2", "l3"],
)

# %%
# plot input over time
_ = sns.lineplot(
    data=df.melt(
        id_vars=["timestamp"], value_vars=["l1", "l2", "l3"], var_name="measurement"
    ),
    x="timestamp",
    y="value",
    hue="measurement",
)

# %%
# plot output over time
_ = sns.lineplot(
    data=output_df.reset_index().melt(
        id_vars=["index"], value_vars=["l1", "l2", "l3"], var_name="measurement"
    ),
    x="index",
    y="value",
    hue="measurement",
)

# %%
new_input = torch.tensor([[230, 230, 230]], dtype=torch.float32)
# %%
out, hidden = lstm(new_input.view(1, 1, -1), hidden)
# %%
out
# %%

# %%
# export trained model
torch.save(lstm.state_dict(), "model.pt")
# %%
# load trained model
lstm = nn.LSTM(input_size=3, hidden_size=3,
               num_layers=1, batch_first=True)  # Input dim is 3, output dim is 3
lstm.load_state_dict(torch.load("model.pt"))
# %%
# put the l1, l2, l3 in a list of tensors
new_input = torch.tensor([[233, 240, 231]], dtype=torch.float32)
new_input = torch.cat([new_input]).view(len(new_input), 1, -1)
hidden = (torch.randn(1, 1, 3), torch.randn(1, 1, 3))  # clean out hidden state
# %%
# normalize inputs using mean 0 and variance 1
normalized_new_input = (new_input - new_input.mean(dim=0)) / new_input.std(dim=0)
# %%
out, hidden = lstm(normalized_new_input, hidden)
# %%
out
# %%
